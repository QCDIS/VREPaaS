param(
    [string]$browser_process_filter = '',               # record resource usage for browser. use this param to specify re pattern to filter browser processes from ps entries
    [switch]$JupyterLab_backend = $false,               # record resource usage for JupyterLab backend
    [switch]$RStudio_backend = $false,                  # record resource usage for RStudio backend
    [alias('v')][string]$vreapi_process_filter = '',    # record resource usage for vreapi [common backend]. use this param to specify re pattern to filter vreapi process from ps entries
    [alias('d')][string]$database_process_filter = '',  # record resource usage for db. use this param to specify re pattern to filter db processes from ps entries
    [alias('vp')][string]$vreapi_pod_filter = '',       # record resource usage for vreapi pod [common backend]. use this param to specify re pattern to filter vreapi pod from kubectl top pod entries
    [alias('dp')][string]$database_pod_filter = '',     # record resource usage for db pod [common backend]. use this param to specify re pattern to filter db pod from kubectl top pod entries
    [string]$log_dir = '.log',                          # directory to store log files
    [Double]$interval = 1,                              # interval between 2 adjacent resource usage captures [seconds]
    [long]$number_of_records = 0,                       # 0 or negative means infinite records. positive means number of records to capture
    [switch]$console = $false                           # print usage data to console
)

# intro messages before recording
if ($console) {
    Write-Host -NoNewline 'Recording CPU & mem usage at '
    Write-Host -NoNewline -ForegroundColor Green 'console'
    Write-Host -NoNewline ' every '
    Write-Host -NoNewline -ForegroundColor Green $interval
    Write-Host ' second(s) ...'
} else {
    if ((Test-Path $log_dir) -eq $false) { & '/usr/bin/mkdir' -p $log_dir }

    $date = Get-Date -Format 'yyyyMMdd-HHmmss'
    $raw_log_file = $log_dir + "/$date.raw.csv"
    $cooked_log_file = $log_dir + "/$date.cooked.csv"

    Write-Host -NoNewline 'Recording CPU & mem usage at '
    Write-Host -NoNewline -ForegroundColor Green $raw_log_file
    Write-Host -NoNewline ' and '
    Write-Host -NoNewline -ForegroundColor Green $cooked_log_file
    Write-Host -NoNewline ' every '
    Write-Host -NoNewline -ForegroundColor Green $interval
    Write-Host ' second(s) ...'
}

class Process_CPU_Entry { # pidstat used here. ps shows average CPU util only while top always show units like m, g, t, p for mem util thus less precise
    # columns for CPU util: [time], UID, PID, %usr, %system, %guest, %wait, %CPU, CPU, Command
    [DateTime]$time
    [int]$UID = -1
    [int]$PID = -1
    [double]${%usr} = 0
    [double]${%system} = 0
    [double]${%guest} = 0
    [double]${%wait} = 0
    [double]${%CPU} = 0
    [int]$CPU = 0
    [string]$Command = ''
    Process_CPU_Entry([DateTime]$time, [int]$UID, [int]$PID, [double]${%usr}, [double]${%system}, [double]${%guest}, [double]${%wait}, [double]${%CPU}, [int]$CPU, [string]$Command) {
        $this.time = $time
        $this.UID = $UID
        $this.PID = $PID
        $this.${%usr} = ${%usr}
        $this.${%system} = ${%system}
        $this.${%guest} = ${%guest}
        $this.${%wait} = ${%wait}
        $this.${%CPU} = ${%CPU}
        $this.CPU = $CPU
        $this.Command = $Command
    }
}

class Process_Memory_Entry {
    # columns for mem util: [time], UID, PID, minflt/s, majflt/s, VSZ, RSS, %MEM, Command
    [DateTime]$time
    [int]$UID = -1
    [int]$PID = -1
    [double]${minflt/s} = 0
    [double]${majflt/s} = 0
    [int]$VSZ = 0 # in KiB
    [int]$RSS = 0 # in KiB
    [double]${%MEM} = 0
    [string]$Command = ''
    Process_Memory_Entry([DateTime]$time, [int]$UID, [int]$PID, [double]${minflt/s}, [double]${majflt/s}, [int]$VSZ, [int]$RSS, [double]${%MEM}, [string]$Command) {
        $this.time = $time
        $this.UID = $UID
        $this.PID = $PID
        $this.${minflt/s} = ${minflt/s}
        $this.${majflt/s} = ${majflt/s}
        $this.VSZ = $VSZ
        $this.RSS = $RSS
        $this.${%MEM} = ${%MEM}
        $this.Command = $Command
    }
}

class Resource_Metric { # for what are sent by K8s metrics server, and cooked entries
    [double]$CPU # %
    [double]$mem # Mi
    Resource_Metric() {
        $this.CPU = 0
        $this.mem = 0
    }
    Resource_Metric([double]$cpu, [double]$mem) {
        $this.CPU = $cpu
        $this.mem = $mem
    }
}

if ((-not $console) -and (-not (Test-Path $raw_log_file))) { (@('time') + [Process_CPU_Entry]::col_name) -join ',' | Out-File $raw_log_file } # add csv headers first

# columns of each row
$cooked_entry = [PSCustomObject]@{
    "time" = $null
}
$CPU_headers = New-Object System.Collections.Generic.List[string]
$mem_headers = New-Object System.Collections.Generic.List[string]
if ($browser_process_filter -ne '') {
    $CPU_headers += "CPU:browser:$browser_process_filter"
    $mem_headers += "mem:browser:$browser_process_filter"
}
if ($JupyterLab_backend) {
    $CPU_headers += "CPU:JupyterLab backend"
    $mem_headers += "mem:JupyterLab backend"
}
if ($RStudio_backend) {
    $CPU_headers += "CPU:RStudio backend"
    $mem_headers += "mem:RStudio backend"
}
if ($vreapi_process_filter -ne '') {
    $CPU_headers += "CPU:vreapi:$vreapi_process_filter"
    $mem_headers += "mem:vreapi:$vreapi_process_filter"
}
if ($database_process_filter -ne '') {
    $CPU_headers += "CPU:database:$database_process_filter"
    $mem_headers += "mem:database:$database_process_filter"
}
if ($vreapi_pod_filter -ne '') {
    $vreapi_pod_filter = ((kubectl get pod | Select-String $vreapi_pod_filter).Line -split '\s+')[0]
    $CPU_headers += "CPU:pod:$vreapi_pod_filter"
    $mem_headers += "mem:pod:$vreapi_pod_filter"
}
if ($database_pod_filter -ne '') {
    $database_pod_filter = ((kubectl get pod | Select-String $database_pod_filter).Line -split '\s+')[0]
    $CPU_headers += "CPU:pod:$database_pod_filter"
    $mem_headers += "mem:pod:$database_pod_filter"
}
$CPU_headers + $mem_headers | ForEach-Object { $cooked_entry | Add-Member -MemberType NoteProperty -Name $_ -Value $null }
if ((-not $console) -and (-not (Test-Path $cooked_log_file))) { $cooked_entry | ConvertTo-Csv | Select-Object -First 1 | Out-File $cooked_log_file } # add csv headers first

$time_format = 'yyyy-MM-dd HH:mm:ss.fff'
$loop_body = {
    $time = Get-Date -Format $time_format
    $cooked_entry.time = $time
    $process_info = (pidstat -ru -p ALL 0) -join "`n" -split "\n\n" | Select-Object -Skip 1
    $util_rows = New-Object System.Collections.Generic.List[System.Collections.Generic.List[string[]]]
    for ($i = 0; $i -lt 2; ++$i) {
        $raw_rows = $process_info[$i] -split '\n' | Select-Object -Skip 1
        $split_rows = New-Object System.Collections.Generic.List[string[]]
        foreach ($raw_row in $raw_rows) {
            $columns = $raw_row -split '\s+'
            $split_rows.Add($columns)
        }
        $util_rows.Add($split_rows)
    }
    if ($browser_process_filter -ne '') {

    }
    Start-Sleep($interval)
}

# main
if ($number_of_records -le 0) {
    while ($true) { & $loop_body }
} else {
    for ($i = 0; $i -lt $number_of_records; ++$i) { & $loop_body }
}
