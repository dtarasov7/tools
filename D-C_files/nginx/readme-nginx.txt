���� ����������� ������ ����������� ��� nginx ����������

���� ������ ��������� �� ����
/opt/VMCluster_deploy_ADL/vmagent/sd/sd_adl_common

� ��� ������ ��������������� ������� 

nginxexporter*.yml

���������� �����: 

- targets: ['<IP_adress_�������_�_�����������>:<����_����������>']
  labels:
    host: <���_�������>
    owner: adl
    env: <���������>

������:
- targets: ['192.168.109.31:9113']
  labels:
    host: nginx1
    owner: adl
    env: dtln-prod


� ������������ nginx ������ ����� ��������� location /status � ����������� "stub_status on;" � ������ Server ������� ������� ���� 8080
���� ���� � localtion  ������, �� ����������� ������ �������������� ���������� � docker-compose ����