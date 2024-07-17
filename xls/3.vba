���������� ������� Word, � ������� ������ ����� ������ �� �������� ����� �������, � ������ ������� ������ (Enter-�� ��������� ����� ������).
� ������� ������� ��� ������ ������ Word � ������ Excel. �� ��������� ��� �� ������� ������� ����� ������� ������, ���������� ������ � �������� �������, ������� ������ �������� ����� �� �������� ������, �������� ��� � ������ Excel � �.�. � ����� ������ ����� ������.

� ���� ���� ��� ���������� ��� ������ �� tbl.Cell(2, 1) ��������� �� ������� excel.

������
Sub OpenWord()
    Dim objWrdApp As Object, objWrdDoc As Object, avFiles, i As Integer, tbl As Object
    avFiles = Application.GetOpenFilename _
                ("Word files(*.doc*),*.do*", 1, "�������� �������", , False)
    If VarType(avFiles) = vbBoolean Then
        Exit Sub
    End If
        Set objWrdApp = CreateObject("Word.Application")
        objWrdApp.Visible = False
        Set objWrdDoc = objWrdApp.Documents.Open(avFiles)
        Set tbl = objWrdDoc.Tables(1)
        ActiveSheet.Cells(1, 1) = tbl.Cell(2, 1).Range.text       
        objWrdDoc.Close True
        objWrdApp.Quit
        Set objWrdDoc = Nothing: Set objWrdApp = Nothing
End Sub
[��������]

[�������� ������� ���������������]
 �������������
Administrator
���������: 2 476
�������
#1

14 ������ 2019, 12:57
������
Sub OpenWord()

    Dim objWrdApp As Object, objWrdDoc As Object, avFiles, tbl As Object
    Dim var, r As Long, i As Long
   
   
    avFiles = Application.GetOpenFilename _
                ("Word files(*.doc*),*.do*", 1, "�������� �������", , False)
    If VarType(avFiles) = vbBoolean Then
        Exit Sub
    End If
   
    Set objWrdApp = CreateObject("Word.Application")
    objWrdApp.Visible = False
    Set objWrdDoc = objWrdApp.Documents.Open(avFiles)
    Set tbl = objWrdDoc.Tables(1)
   
    ' �������� ������ �� ����-������ � ����������.
    var = tbl.Cell(2, 1).Range.Text
    ' ������� � ����� ��� �������. ��� ��� ������� ���� � ������ ����-������.
        ' ���� ������ � ���� ������, ������ ������ ������ �� �����.
    var = Left(var, Len(var) - 2)
    ' ��������� ����� ������ �� ����� �� ������� "������� ������".
    var = Split(var, Chr(13))
    ' ������������� ������ �� ������-����� � ������ ������.
    r = 1
    ' ���������� ����� � ������-������.
    For i = 0 To UBound(var)
        ActiveSheet.Cells(r, 1) = var(i)
        r = r + 1
    Next i
   
    objWrdDoc.Close True
    objWrdApp.Quit
    Set objWrdDoc = Nothing: Set objWrdApp = Nothing
   
End Sub

