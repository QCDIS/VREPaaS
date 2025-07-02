param(
    [string]$browser_process_filter = '',                   # record resource usage for browser. use this param to specify re pattern to filter browser processes from ps entries
    [switch]$JupyterLab_backend = $false,                   # record resource usage for JupyterLab backend
    [switch]$RStudio_backend = $false,                      # record resource usage for RStudio backend
    [alias('v')][string]$vreapi_process_filter = '',        # record resource usage for vreapi [common backend]. use this param to specify re pattern to filter vreapi process from ps entries
    [alias('d')][string]$database_process_filter = '',      # record resource usage for db. use this param to specify re pattern to filter db processes from ps entries
    [alias('vp')][string]$vreapi_pod_filter = '',           # record resource usage for vreapi pod [common backend]. use this param to specify re pattern to filter vreapi pod from kubectl top pod entries
    [alias('dp')][string]$database_pod_filter = '',         # record resource usage for db pod [common backend]. use this param to specify re pattern to filter db pod from kubectl top pod entries
    [string]$log_dir = '.log',                              # directory to store log files
    [Double]$interval = 1,                                  # interval between 2 adjacent resource usage captures [seconds]
    [long]$number_of_records = 0,                           # 0 or negative means infinite records. positive means number of records to capture
    [switch]$console = $false                               # print usage data to console
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

class Process_CPU_Entry { # pidstat [sudo apt install sysstat] used here. ps shows average CPU util only while top always show units like m, g, t, p for mem util thus less precise
    # columns for CPU util: [time], UID, PID, %usr, %system, %guest, %wait, %CPU, CPU, Command
    [DateTime]$time
    [int]$UID = -1
    [int]$PID = -1
    [double]$pct_usr = 0
    [double]$pct_system = 0
    [double]$pct_guest = 0
    [double]$pct_wait = 0
    [double]$pct_CPU = 0
    [int]$CPU = 0
    [string]$Command = ''
    Process_CPU_Entry([DateTime]$time, [int]$UID, [int]$_PID, [double]$pct_usr, [double]$pct_system, [double]$pct_guest, [double]$pct_wait, [double]$pct_CPU, [int]$CPU, [string]$Command) {
        $this.time = $time
        $this.UID = $UID
        $this.PID = $_PID
        $this.pct_usr = $pct_usr
        $this.pct_system = $pct_system
        $this.pct_guest = $pct_guest
        $this.pct_wait = $pct_wait
        $this.pct_CPU = $pct_CPU
        $this.CPU = $CPU
        $this.Command = $Command
    }
}

class Process_Memory_Entry { # pidstat
    # columns for mem util: [time], UID, PID, minflt/s, majflt/s, VSZ, RSS, %MEM, Command
    [DateTime]$time
    [int]$UID = -1
    [int]$PID = -1
    [double]$minflt_p_s = 0
    [double]$majflt_p_s = 0
    [int]$VSZ = 0 # in KiB
    [int]$RSS = 0 # in KiB
    [double]$pct_MEM = 0
    [string]$Command = ''
    Process_Memory_Entry([DateTime]$time, [int]$UID, [int]$_PID, [double]$minflt_p_s, [double]$majflt_p_s, [int]$VSZ, [int]$RSS, [double]$pct_MEM, [string]$Command) {
        $this.time = $time
        $this.UID = $UID
        $this.PID = $_PID
        $this.minflt_p_s = $minflt_p_s
        $this.majflt_p_s = $majflt_p_s
        $this.VSZ = $VSZ
        $this.RSS = $RSS
        $this.pct_MEM = $pct_MEM
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
if ($env:LC_NUMERIC -eq $null) {
    $culture = [System.Globalization.CultureInfo]::CurrentCulture.Name
} else {
    $BCP_47_culture_name_for_pidstat = $env:LC_NUMERIC.Substring(0, $env:LC_NUMERIC.IndexOf('.')) # e.g. en-US, nl-NL
    $culture = New-Object System.Globalization.CultureInfo($BCP_47_culture_name_for_pidstat)
}
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
    $CPU_util_rows = $util_rows[0]
    $mem_util_rows = $util_rows[1]
    $CPU_entries = New-Object System.Collections.Generic.List[Process_CPU_Entry]
    $mem_entries = New-Object System.Collections.Generic.List[Process_Memory_Entry]
    foreach ($seg in $CPU_util_rows) {
        $e = [Process_CPU_Entry]::new(
            [DateTime]::ParseExact($time, $time_format, $null),
            [int]($seg[1]),
            [int]($seg[2]),
            [double]::Parse($seg[3], $culture),
            [double]::Parse($seg[4], $culture),
            [double]::Parse($seg[5], $culture),
            [double]::Parse($seg[6], $culture),
            [double]::Parse($seg[7], $culture),
            [int]($seg[8]),
            $seg[9..($seg.Length - 1)] -join ' '
        )
        $CPU_entries.Add($e)
    }
    foreach ($seg in $mem_util_rows) {
        $e = [Process_Memory_Entry]::new(
            [DateTime]::ParseExact($time, $time_format, $null),
            [int]($seg[1]),
            [int]($seg[2]),
            [double]::Parse($seg[3], $culture),
            [double]::Parse($seg[4], $culture),
            [int]($seg[5]),
            [int]($seg[6]),
            [double]::Parse($seg[7], $culture),
            $seg[8..($seg.Length - 1)] -join ' '
        )
        $mem_entries.Add($e)
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
