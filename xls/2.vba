Sub ReadTable()

    Dim objWrdApp As Object
    Dim objWrdDoc As Object
    Dim Arr(3, 3)
    
    On Error Resume Next
    
    Set objWrdApp = GetObject(, "Word.Application")
    
    If objWrdApp Is Nothing Then
        Set objWrdApp = CreateObject("Word.Application")
        objWrdApp.Visible = False
    End If
    Set objWrdDoc = objWrdApp.Documents.Open("Ваш путь\ваш файл.docx")
    
    Set tbl = objWrdDoc.tables(1)
    For i = 1 To 3
         For j = 1 To 3
              Cells(i, j) = Val(tbl.Cell(i, j).Range.Text)
         Next j
    Next i
    
    ' и так 4 раза
    
    Set objWrdDoc = Nothing
    Set objWrdApp = Nothing

End Sub
