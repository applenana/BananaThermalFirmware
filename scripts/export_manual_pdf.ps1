param(
    [Parameter(Mandatory = $true)][string]$InputDocx,
    [Parameter(Mandatory = $true)][string]$OutputPdf
)
$ErrorActionPreference = 'Stop'
$taskInput = (Resolve-Path -LiteralPath $InputDocx).Path
$taskOutput = [System.IO.Path]::GetFullPath($OutputPdf)
$taskWord = $null
$taskDocument = $null
try {
    # A separate invisible Word instance; never attach to a user's active document.
    $taskWord = New-Object -ComObject Word.Application
    $taskWord.Visible = $false
    $taskWord.DisplayAlerts = 0
    $taskWord.AutomationSecurity = 3
    $taskDocument = $taskWord.Documents.Open($taskInput, $false, $true, $false)
    $taskDocument.Repaginate()
    # Preserve internal links, tagged text and heading bookmarks in the PDF.
    $taskDocument.ExportAsFixedFormat($taskOutput, 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $false)
    Write-Output $taskOutput
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
