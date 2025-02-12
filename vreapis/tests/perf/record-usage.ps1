param(
    [string]$browser_cmd = $null,
    [switch]$jupyterlab_backend = $false,
    [switch]$rstudio_backend = $false,
    [string]$pod_name = $null,
    [string]$log_dir = '.log',
    [Double]$interval = 1
)

if ((Test-Path $log_dir) -eq $false) {
    & '/usr/bin/mkdir' -p $log_dir
}

$pod_name = ((kubectl get pod | Select-String $pod_name).Line -split '\s+')[0]

$log_file = $log_dir + "/$pod_name.$(Get-Date -Format 'yyyyMMdd-HHmmss').csv"

Write-Host -NoNewline 'Recording CPU & mem usage of pod '
Write-Host -NoNewline -ForegroundColor Green $pod_name
Write-Host -NoNewline ' to '
Write-Host -NoNewline -ForegroundColor Green $log_file
Write-Host -NoNewline ' every '
Write-Host -NoNewline -ForegroundColor Green $interval
Write-Host ' second(s) ...'

class Pod_Metric {
    [string]$time = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss.fff')
    [string]$CPU
    [string]$mem

    Pod_Metric([string]$cpu, [string]$mem) {
        $this.CPU = $cpu
        $this.mem = $mem
    }
}

while ($true) {
    $entry = kubectl top pod $pod_name --no-headers | ForEach-Object {
        $col = $_ -split '\s+'
        [Pod_Metric]::new($col[1], $col[2])
    }
    $entry | Export-Csv -Append $log_file
    Start-Sleep $interval
}
