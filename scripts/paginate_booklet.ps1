param(
    [Parameter(Mandatory = $true)][string]$InputDocx,
    [Parameter(Mandatory = $true)][string]$OutputJson,
    [Parameter(Mandatory = $true)][string]$OutputPdf
)
$ErrorActionPreference = 'Stop'
$taskWord = $null
$taskDocument = $null
try {
    $taskWord = New-Object -ComObject Word.Application
    $taskWord.Visible = $false
    $taskWord.DisplayAlerts = 0
    $taskWord.AutomationSecurity = 3
    $taskDocument = $taskWord.Documents.Open($InputDocx, $false, $true, $false)
    $taskDocument.Repaginate()
    $taskRecords = @()
    foreach ($taskBookmark in $taskDocument.Bookmarks) {
        if ($taskBookmark.Name -like 'block*' -or $taskBookmark.Name -like 'row*') {
            $taskRange = $taskBookmark.Range.Duplicate
            $taskRange.Collapse(1)
            $taskRecords += [pscustomobject]@{
                name = $taskBookmark.Name
                page = $taskRange.Information(3)
                y = $taskRange.Information(6)
            }
        }
    }
    $taskPages = $taskDocument.ComputeStatistics(2)
    $taskResult = [pscustomobject]@{ pages = $taskPages; blocks = $taskRecords }
    $taskResult | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $OutputJson -Encoding utf8
    $taskDocument.ExportAsFixedFormat($OutputPdf, 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $false)
    Write-Output "Pages: $taskPages"
} finally {
    if ($null -ne $taskDocument) {
        $taskSaveOption = 0
        $taskDocument.Close([ref]$taskSaveOption)
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskDocument)
    }
    if ($null -ne $taskWord) {
        $taskSaveOption = 0
        $taskWord.Quit([ref]$taskSaveOption)
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskWord)
    }
}
