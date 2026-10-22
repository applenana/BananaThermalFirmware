param(
    [Parameter(Mandatory = $true)][string]$InputDocx,
    [Parameter(Mandatory = $true)][string]$OutputJson,
    [Parameter(Mandatory = $true)][double]$SheetWidthMm,
    [Parameter(Mandatory = $true)][double]$SheetHeightMm
)
$ErrorActionPreference = 'Stop'
$taskWord = $null
$taskDocument = $null
$taskStage = 'start'
try {
    $taskStage = 'create Word'
    $taskWord = New-Object -ComObject Word.Application
    $taskWord.Visible = $false
    $taskWord.DisplayAlerts = 0
    $taskWord.AutomationSecurity = 3
    $taskStage = 'open document'
    $taskDocument = $taskWord.Documents.Open($InputDocx, $false, $true, $false)
    $taskBefore = $taskDocument.ComputeStatistics(2)
    $taskSetups = @()
    foreach ($taskSection in $taskDocument.Sections) {
        $taskSetup = $taskSection.PageSetup
        # Keep Word's native default for all pages in one booklet. The original
        # package has no bookFoldPrintingSheets override; see MS-OE376 2.1.398.
        $taskSetup.Orientation = 1
        $taskStage = 'set paper width'
        $taskSetup.PageWidth = $SheetWidthMm * 72 / 25.4
        $taskStage = 'set paper height'
        $taskSetup.PageHeight = $SheetHeightMm * 72 / 25.4
    }
    $taskStage = 'enable document BookFoldPrinting after paper size'
    $taskDocument.PageSetup.BookFoldPrinting = $true
    foreach ($taskSection in $taskDocument.Sections) {
        $taskSetup = $taskSection.PageSetup
        $taskSetups += [pscustomobject]@{
            bookFold = $taskSetup.BookFoldPrinting
            paperWidthMm = $taskSetup.PageWidth * 25.4 / 72
            paperHeightMm = $taskSetup.PageHeight * 25.4 / 72
            gutterMm = $taskSetup.Gutter * 25.4 / 72
            bookletPages = $taskSetup.BookFoldPrintingSheets
        }
    }
    $taskDocument.Repaginate()
    $taskAfter = $taskDocument.ComputeStatistics(2)
    [pscustomobject]@{
        input = $InputDocx
        beforePages = $taskBefore
        afterPages = $taskAfter
        sections = $taskSetups
        saved = $false
        printed = $false
    } | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $OutputJson -Encoding utf8
    Write-Output "Book fold check: $taskBefore -> $taskAfter pages"
} catch {
    throw "Word booklet stage '$taskStage': $($_.Exception.Message)"
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
