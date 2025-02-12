# duplicate rmd test files for test repetitions
# At present, Cell Containerizer from NaaVRE automatically generates Docker image name for a cell using login username and its 1st line comment. To bring more convenience to test repetitions, this script directly duplicates designated test files with suffix added to the 1st line comment.

param(
    [Parameter(Mandatory = $true)][System.IO.FileInfo[]]$pathnames,
    [int]$copies = 10,
    [string]$extension_prefix_prefix = '.',
    [string]$extension_prefix_suffix = '',
    [string]$magic_prefix = ' # C25B14E054D65738 [rpt ',
    [string]$magic_suffix = '] '
)

foreach ($pathname in $pathnames) {
    $content = Get-Content -Raw $pathname
    $re = '((^|[\r\n])```{r[^\r\n]+[\r\n]+(\s#\|[^\r\n]*[\r\n]+)*#[^\r\n]*)' # code chunk header to 1st line comment [chunk options w/ prefix #| skipped]
    # $res = $content | Select-String -AllMatches $re
    # $res.Matches | ForEach-Object { Write-Host $_.Value }
    for ($i = 0; $i -lt $copies; ++$i) {
        $new_content = $content -replace $re, "`$1$magic_prefix$i$magic_suffix"
        Set-Content "$($pathname.DirectoryName)/$($pathname.BaseName)$extension_prefix_prefix$i$extension_prefix_suffix$($pathname.Extension)" $new_content
    }
}
