param([Parameter(Mandatory=$true)][string]$InputDoc,
      [Parameter(Mandatory=$true)][string]$PdfPath)
$ErrorActionPreference='Stop'
$inputPath=(Resolve-Path -LiteralPath $InputDoc).Path
$outputPath=[System.IO.Path]::GetFullPath($PdfPath)
if ([System.IO.Path]::GetExtension($outputPath) -ne '.pdf') { throw 'PdfPath must end in .pdf' }
$null=New-Item -ItemType Directory -Path ([System.IO.Path]::GetDirectoryName($outputPath)) -Force
$word=$null
$doc=$null
try {
 $word=New-Object -ComObject Word.Application
 $word.Visible=$false
 $word.DisplayAlerts=0
 $doc=$word.Documents.Open($inputPath,$false,$false)
 $doc.Repaginate()
 $null=$doc.Fields.Update()
 foreach($toc in $doc.TablesOfContents) {$toc.Update()}
 # Touch only the field-end neighborhood, never iterate every document paragraph.
 foreach($toc in $doc.TablesOfContents) {
  $paragraph=$doc.Range([Math]::Max(0,$toc.Range.End-1),$toc.Range.End).Paragraphs.Last
  for($n=0;$n -lt 3 -and $null -ne $paragraph;$n++) {
   if ($paragraph.Range.Text.Trim([char]13,[char]7,[char]12,[char]32) -eq '') {
    $paragraph.Range.Font.Size=1
    $paragraph.Format.SpaceBefore=0
    $paragraph.Format.SpaceAfter=0
    $paragraph.Format.LineSpacingRule=4
    $paragraph.Format.LineSpacing=1
   }
   $paragraph=$paragraph.Next()
  }
 }
 $doc.Repaginate()
 foreach($toc in $doc.TablesOfContents) {$toc.UpdatePageNumbers()}
 $doc.Save()
 $doc.ExportAsFixedFormat($outputPath,17)
 @{pages=$doc.ComputeStatistics(2);toc=$doc.TablesOfContents.Count;tables=$doc.Tables.Count;images=$doc.InlineShapes.Count} | ConvertTo-Json -Compress
} finally {
 if ($null -ne $doc) { $doc.Close(0) }
 if ($null -ne $word) { $word.Quit() }
}
