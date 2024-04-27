���� ����������� ������ ����������� ��� blackbox ����������

���� ������ ��������� �� ����
/opt/VMCluster_deploy_ADL/vmagent/sd/sd_adl_blackbox/

� ��� ������ ��������������� �������:

- 2xx*.yml  - http ��� https ������ � �������� ���� 200-299
- 401*.yml  - http ��� https ������ � �������� ���� 401
- tcp*.yml  - ������������� tcp ����������
- icmp*.yml  - ping


C��������� �����:

2xx*.yml  

- targets: ['<http|https>://<IP_adress_�������>:<����_�������>/<����>']
  labels:
    host: <���_�������>
    application: <���_�������>
    owner: adl
    env: <���������>

������:
- targets: ['https://10.80:5601/app/login?nextUrl=%2F']
  labels:
    host: prod-odfe01
    application: kibana
    owner: ctp
    env: dtln-prod



tcp*.yml

������ tcp:
- targets: ['10.80:5601']
  labels:
    host: prod-odfe01
    application: kibana
    owner: ctp
    env: dtln-prod



icmp*.yml

������ icmp:
- targets: ['10.80']
  labels:
    host: prod-odfe01
    owner: ctp
    env: dtln-prod
