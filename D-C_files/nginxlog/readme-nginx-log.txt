���� ����������� ������ ����������� ��� nginxlog ����������

���� ������ ��������� �� ����
/opt/VMCluster_deploy_ADL/vmagent/sd/sd_adl_common

� ��� ������ �������������� ������� 

nginxlog*.yml

���������� �����

- targets: ['<IP_adress_�������_�_�����������>:<����_����������>']
  labels:
    host: <���_�������>
    owner: adl
    env: <���������>

������:
- targets: ['192.168.109.31:4040']
  labels:
    host: elasticsearch1
    owner: adl
    env: dtln-preprod

���������������� ���� ���������� �������� �� ����������� (combined) ������ access ���� nginx
��� ������������� ����������� ������� access ��� ����� - ���������� ������ ���������� � ���� ������� ����������
