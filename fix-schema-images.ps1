# fix-schema-images.ps1
# Scans all .html files recursively for Article/TechArticle/ScholarlyArticle
# JSON-LD blocks missing an "image" field, and fills it in using that page's
# existing <meta property="og:image"> tag.
#
# Does NOT touch datePublished or author -- those need a real value, not a
# guessed one. Those gaps are only reported.
#
# Usage: run from the repo root:
#   .\fix-schema-images.ps1

$articleTypes = @("Article", "TechArticle", "ScholarlyArticle", "NewsArticle", "BlogPosting")
$files = Get-ChildItem -Recurse -Filter *.html
$fixedCount = 0
$stillMissing = @()

foreach ($file in $files) {
    $html = Get-Content $file.FullName -Raw -Encoding UTF8

    $ogImageMatch = [regex]::Match($html, '<meta property="og:image" content="([^"]+)"')
    $ogImage = if ($ogImageMatch.Success) { $ogImageMatch.Groups[1].Value } else { $null }

    $blockMatches = [regex]::Matches($html, '<script type="application/ld\+json">(.*?)</script>', [System.Text.RegularExpressions.RegexOptions]::Singleline)
    if ($blockMatches.Count -eq 0) { continue }

    $changed = $false
    $newHtml = $html

    foreach ($m in $blockMatches) {
        $raw = $m.Groups[1].Value
        try {
            $data = $raw | ConvertFrom-Json
        } catch {
            Write-Host "PARSE FAILED: $($file.FullName) -- $($_.Exception.Message)"
            continue
        }

        $items = if ($data -is [System.Array]) { $data } else { @($data) }

        $blockChanged = $false

        foreach ($item in $items) {
            if (-not ($item.PSObject.Properties.Name -contains '@type')) { continue }
            $types = @($item.'@type')
            $isArticle = $false
            foreach ($t in $types) { if ($articleTypes -contains $t) { $isArticle = $true } }
            if (-not $isArticle) { continue }

            if (-not ($item.PSObject.Properties.Name -contains 'image')) {
                if ($ogImage) {
                    $item | Add-Member -NotePropertyName 'image' -NotePropertyValue $ogImage -Force
                    $blockChanged = $true
                    $changed = $true
                } else {
                    $stillMissing += [PSCustomObject]@{ File = $file.FullName; Field = 'image'; Reason = 'no og:image found to copy from' }
                }
            }

            if (-not ($item.PSObject.Properties.Name -contains 'datePublished')) {
                $stillMissing += [PSCustomObject]@{ File = $file.FullName; Field = 'datePublished'; Reason = 'needs a real date, not auto-fixed' }
            }

            if (-not ($item.PSObject.Properties.Name -contains 'author')) {
                $stillMissing += [PSCustomObject]@{ File = $file.FullName; Field = 'author'; Reason = 'needs a real value, not auto-fixed' }
            }
        }

        if ($blockChanged) {
            $newBlock = $data | ConvertTo-Json -Depth 20
            $newHtml = $newHtml.Replace($raw, $newBlock)
        }
    }

    if ($changed) {
        Set-Content -Path $file.FullName -Value $newHtml -Encoding UTF8 -NoNewline
        $fixedCount++
        Write-Host "FIXED image: $($file.FullName)"
    }
}

Write-Host ""
Write-Host "$fixedCount file(s) updated with 'image' field."

if ($stillMissing.Count -gt 0) {
    Write-Host ""
    Write-Host "$($stillMissing.Count) field(s) still need manual attention:"
    $stillMissing | ForEach-Object { Write-Host "  $($_.File) :: missing '$($_.Field)' ($($_.Reason))" }
}
