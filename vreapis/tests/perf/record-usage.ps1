param(
    [string]$browser_program_name = $null,  # record resource usage for browser. use this param to specify re pattern for browser pathname
    [switch]$JupyterLab_backend = $false,   # record resource usage for JupyterLab backend
    [switch]$RStudio_backend = $false,      # record resource usage for RStudio backend
    [string]$pod_name = $null,              # record resource usage for pod [common backend]. use this param to specify re pattern for pod name
    [string]$log_dir = '.log',              # directory to store log files
    [Double]$interval = 1                   # interval between 2 adjacent resource usage captures [seconds]
)

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

class Simplified_ps_Entry {
    static [string] $header_row = 'user,pid,%cpu,rss,command' # complete header row: 'USER,PID,%CPU,%MEM,VSZ,RSS,TTY,STAT,START,TIME,COMMAND'
    static [string[]] $col_name = [Simplified_ps_Entry]::header_row -replace '%', '' -split ','
    static $col_name_index = @{}
    static [void] Init() {
        for ([int]$i = 0; $i -lt [Simplified_ps_Entry]::col_name.Count; ++$i) {
            [Simplified_ps_Entry]::col_name_index[[Simplified_ps_Entry]::col_name[$i]] = $i
        }
    }
    [string]$time = ''
    [string]$USER = ''
    [int]$PID = -1
    [double]$CPU = 0.0
    [int]$RSS = 0 # KB
    [string]$COMMAND = ''
    [void]constructor([string]$user, [int]$process_ID, [double]$cpu, [int]$rss, [string]$command) {
        $this.USER = $user
        $this.PID = $process_ID
        $this.CPU = $cpu
        $this.RSS = $rss
        $this.COMMAND = $command
    }
    Simplified_ps_Entry([string]$time, [string]$user, [int]$process_ID, [double]$cpu, [int]$rss, [string]$command) {
        $this.time = $time
        $this.constructor($user, $process_ID, $cpu, $rss, $command)
    }
    [void]constructor([string]$raw_entry) {
        $cooked_entry = $raw_entry -split '\s+'
        $this.USER = $cooked_entry[[Simplified_ps_Entry]::col_name_index['user']]
        $this.PID = [int]$cooked_entry[[Simplified_ps_Entry]::col_name_index['pid']]
        $this.CPU = [double]$cooked_entry[[Simplified_ps_Entry]::col_name_index['cpu']]
        $this.RSS = [int]$cooked_entry[[Simplified_ps_Entry]::col_name_index['rss']]
        $this.COMMAND = $cooked_entry[[Simplified_ps_Entry]::col_name_index['command']..($cooked_entry.count - 1)]
    }
    Simplified_ps_Entry([string]$time, [string]$raw_entry) {
        $this.time = $time
        $this.constructor($raw_entry)
    }
}
[Simplified_ps_Entry]::Init()

class Resource_Metric {
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

if (-not (Test-Path $raw_log_file)) { (@('time') + [Simplified_ps_Entry]::col_name) -join ',' | Out-File $raw_log_file } # add csv headers first

$compound_resource_metric = [PSCustomObject]@{
    "time" = $null
}
$cpu_headers = $mem_headers = @()
if ($browser_program_name -ne $null) {
    $cpu_headers += "CPU:browser:$browser_program_name"
    $mem_headers += "mem:browser:$browser_program_name"
}
if ($JupyterLab_backend) {
    $cpu_headers += "CPU:JupyterLab backend"
    $mem_headers += "mem:JupyterLab backend"
}
if ($RStudio_backend) {
    $cpu_headers += "CPU:RStudio backend"
    $mem_headers += "mem:RStudio backend"
}
if ($pod_name -ne $null) {
    $pod_name = ((kubectl get pod | Select-String $pod_name).Line -split '\s+')[0]
    $cpu_headers += "CPU:pod:$pod_name"
    $mem_headers += "mem:pod:$pod_name"
}
$cpu_headers + $mem_headers | ForEach-Object { $compound_resource_metric | Add-Member -MemberType NoteProperty -Name $_ -Value $null }
if (-not (Test-Path $cooked_log_file)) { $compound_resource_metric | ConvertTo-Csv | Select-Object -First 1 | Out-File $cooked_log_file } # add csv headers first

$ps_pathname = '/usr/bin/ps'
$time_format = 'yyyy-MM-dd HH:mm:ss.fff'

while ($true) {
    $time = Get-Date -Format $time_format
    $compound_resource_metric.time = $time
    $new_raw_ps_entries = New-Object System.Collections.Generic.List[Simplified_ps_Entry]
    if ($browser_program_name -ne $null) {
        $browser_processes = & $ps_pathname 'exo' $([Simplified_ps_Entry]::header_row) | Select-String -a $browser_program_name
        $browser_metric = [Resource_Metric]::new()
        foreach ($process in $browser_processes) {
            $m = [Simplified_ps_Entry]::new($time, $process)
            $new_raw_ps_entries.Add($m)
            $browser_metric.CPU += $m.CPU
            $browser_metric.mem += $m.RSS * 1000 / 1024.0
        }
        $compound_resource_metric."CPU:browser:$browser_program_name" = $browser_metric.CPU
        $compound_resource_metric."mem:browser:$browser_program_name" = $browser_metric.mem
    }
    if ($JupyterLab_backend) {
        $JupyterLab_backend_processes = & $ps_pathname 'exo' $([Simplified_ps_Entry]::header_row) | Select-String -a 'jupyter.?lab'
        $JupyterLab_backend_metric = [Resource_Metric]::new()
        foreach ($process in $JupyterLab_backend_processes) {
            $m = [Simplified_ps_Entry]::new($time, $process)
            $new_raw_ps_entries.Add($m)
            $JupyterLab_backend_metric.CPU += [double]$m.CPU
            $JupyterLab_backend_metric.mem += [double]$m.RSS * 1000 / 1024.0
        }
        $compound_resource_metric."CPU:JupyterLab backend" = $JupyterLab_backend_metric.CPU
        $compound_resource_metric."mem:JupyterLab backend" = $JupyterLab_backend_metric.mem
    }
    if ($RStudio_backend) {
        $RStudio_backend_processes = & $ps_pathname 'axo' $([Simplified_ps_Entry]::header_row) | Select-String -a 'rstudio-server' # here 'axo' not 'exo' since all process got by the latter are contained in those got by the former
        $RStudio_backend_metric = [Resource_Metric]::new()
        foreach ($process in $RStudio_backend_processes) {
            $m = [Simplified_ps_Entry]::new($time, $process)
            $new_raw_ps_entries.Add($m)
            $RStudio_backend_metric.CPU += [double]$m.CPU
            $RStudio_backend_metric.mem += [double]$m.RSS * 1000 / 1024.0
        }
        $compound_resource_metric."CPU:RStudio backend" = $RStudio_backend_metric.CPU
        $compound_resource_metric."mem:RStudio backend" = $RStudio_backend_metric.mem
    }
    if ($pod_name -ne $null) {
        $pod_metric = kubectl top pod $pod_name --no-headers | ForEach-Object {
            $col = $_ -split '\s+'
            [Resource_Metric]::new([double]($col[1].substring(0, $col[1].Length - 'm'.Length)) / 10.0, [double]($col[2]).substring(0, $col[2].Length - 'Mi'.Length))
        }
        $compound_resource_metric."CPU:pod:$pod_name" = $pod_metric.CPU
        $compound_resource_metric."mem:pod:$pod_name" = $pod_metric.mem
    }
    $new_raw_ps_entries | Export-Csv -Append $raw_log_file
    $compound_resource_metric | Export-Csv -Append $cooked_log_file
    Start-Sleep($interval)
}
