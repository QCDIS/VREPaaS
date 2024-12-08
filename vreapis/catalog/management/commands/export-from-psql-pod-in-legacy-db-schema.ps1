$project_root = Resolve-Path "$PSScriptRoot/../../.."

$vreapi_pod_inf = kubectl get pod | sls '^vrepaas-vreapi-\w+-\w+'
$vreapi_pod_name = $vreapi_pod_inf.Matches.Value
$psql_pod_inf = kubectl get pod -owide | sls '^vrepaas-postgresql-0'
$psql_pod_IP = ($psql_pod_inf.Line | sls '\d+\.\d+\.\d+\.\d+').Matches.Value

cd $project_root
$var = Get-Content export_VARS
$off_DB_HOST = ($var | sls '^export DB_HOST=').LineNumber - 1
$off_DB_NAME = ($var | sls '^export DB_NAME=').LineNumber - 1
$off_DB_USER = ($var | sls '^export DB_USER=').LineNumber - 1
$off_DB_PASSWORD = ($var | sls '^export DB_PASSWORD=').LineNumber - 1
$var[$off_DB_HOST] = "export DB_HOST=$psql_pod_IP"
$var[$off_DB_NAME] = "export DB_NAME=vrepaas"
$var[$off_DB_USER] = "export DB_USER=vrepaas"
$var[$off_DB_PASSWORD] = "export DB_PASSWORD=vrepaas"

$var > /tmp/export_VARS
kubectl cp /tmp/export_VARS "${vreapi_pod_name}:/tmp"
kubectl cp "$PSScriptRoot/export-from-psql-pod-in-legacy-db-schema.sh" "${vreapi_pod_name}:/tmp"
kubectl exec -it $vreapi_pod_name -- bash "/tmp/export-from-psql-pod-in-legacy-db-schema.sh"

kubectl cp "${vreapi_pod_name}:/app/NaaVRE_db.json" $project_root/NaaVRE_db.json
