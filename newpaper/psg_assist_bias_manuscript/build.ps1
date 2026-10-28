# Regenerate the manuscript's values, tables and figures from the committed reports, then build supplement.pdf and
# main.pdf. The supplement is built first, because main.tex takes the supplementary table numbers from
# generated/supplement_refs.tex, which is written from supplement.aux.
# Uses pdflatex and BibTeX directly: MiKTeX's latexmk needs a Windows Perl, which is not installed.
$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$env:PYTHONPATH = Join-Path $root "src"
python -m careport.psg_assist_manuscript
if ($LASTEXITCODE -ne 0) { Write-Error "asset generation failed"; exit 1 }
Push-Location $PSScriptRoot
try {
    foreach ($doc in @("supplement", "main")) {
        if ($doc -eq "main") {
            python -m careport.psg_assist_manuscript --supplement-refs
            if ($LASTEXITCODE -ne 0) { Write-Error "supplement references failed"; exit 1 }
        }
        pdflatex -interaction=nonstopmode "$doc.tex" | Out-Null
        bibtex $doc | Out-Null
        pdflatex -interaction=nonstopmode "$doc.tex" | Out-Null
        pdflatex -interaction=nonstopmode "$doc.tex" | Out-Null
        $problems = Select-String -Path "$doc.log" -Pattern '^!|Undefined value|Citation .* undefined|Reference .* undefined'
        if ($problems) { $problems | ForEach-Object { $_.Line }; exit 1 }
        Select-String -Path "$doc.log" -Pattern 'Output written' | ForEach-Object { "${doc}: " + $_.Line }
    }
} finally {
    Pop-Location
}
