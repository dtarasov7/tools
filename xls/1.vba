Sub Copy_Word_Tables()
Dim arr As Variant
With Application: .ScreenUpdating = False: .EnableEvents = False: .DisplayAlerts = False: .Calculation = xlManual: End With

'открытие Word-файла
    Set oWord = CreateObject("Word.Application")
    oWord.Visible = True
    Set oDoc = oWord.Documents.Open(ThisWorkbook.Path & "\" & "дизайн.rtf")
    
ThisWorkbook.Sheets(1).UsedRange.ClearContents
rr = 1

'On Error Resume Next
For aTbl = 1 To 4   'oDoc.tables.Count
ReDim arr(1 To oDoc.tables(aTbl).Rows.Count, 1 To oDoc.tables(aTbl).Columns.Count)
    For j = 1 To UBound(arr, 2)
        For i = 1 To UBound(arr, 1)
            arr(i, j) = Trim(Replace(oDoc.tables(aTbl).cell(i, j).Range.Text, Chr(7), ""))
        Next i
    Next j
ThisWorkbook.Sheets(1).Range("A" & rr).Resize(UBound(arr, 1), UBound(arr, 2)).Value = arr
rr = rr + oDoc.tables(aTbl).Rows.Count + 2
arr = Empty
Next

oWord.Quit False
'..................
With Application: .ScreenUpdating = True: .EnableEvents = True: .DisplayAlerts = True: .Calculation = xlAutomatic: End With
MsgBox "Tables loaded"
End Sub
