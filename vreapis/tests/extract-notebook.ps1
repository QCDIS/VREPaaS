param(
    [System.IO.FileInfo[]]$input_files,
    [System.IO.FileInfo]$output_dir
)
New-Item -i Directory -f $output_dir
foreach ($input_file in $input_files) {
    $root = ConvertFrom-Json (Get-Content -raw $input_file) -d 100
    $serialized_nb = ConvertTo-Json $root.data.notebook -d 100
    $serialized_nb > $output_dir/$($input_file.BaseName).ipynb
    switch ($root.data.kernel) {
        'ipython' {}
        'IRkernel' {
            $serialized_nb | jupytext --from ipynb --to Rmd > $output_dir/$($input_file.BaseName).Rmd
        }
    }
}
