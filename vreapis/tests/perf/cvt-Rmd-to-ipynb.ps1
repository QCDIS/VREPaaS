param(
    [System.IO.FileInfo[]]$pathnames,   # files to convert
#    $kernelspec = @{
#        display_name = 'R [conda env:jupyterlab] *'
#        language = 'R'
#        name = 'conda-env-jupyterlab-r'
#    }
    $kernelspec = @{
        display_name = 'R'
        language = 'R'
        name = 'ir'
    },
    $language_info = @{
        codemirror_mode = 'r'
        file_extension = '.r'
        mimetype = 'text/x-r-source'
        name = 'R'
        pygments_lexer = 'r'
#        version = '4.3.3'
        version = '4.4.1'
    }
)


foreach ($pathname in $pathnames) {
    Write-Host -NoNewline "src: "
    Write-Host -ForegroundColor Yellow $pathname
    $dst = "$($pathname.DirectoryName)/$($pathname.BaseName).ipynb"
    Get-Content -Raw $pathname | jupytext --from Rmd --to ipynb --opt split_at_heading=true -o - > $dst
    $generated_ipynb = ConvertFrom-Json (Get-Content $dst -Raw)
    $generated_ipynb.metadata | Add-Member -NotePropertyName kernelspec -NotePropertyValue $kernelspec
    $generated_ipynb.metadata | Add-Member -NotePropertyName language_info -NotePropertyValue $language_info
    $generated_ipynb | ConvertTo-Json -Depth 100 | Set-Content $dst
    Write-Host -NoNewline "dst: "
    Write-Host -ForegroundColor Green $dst
}
