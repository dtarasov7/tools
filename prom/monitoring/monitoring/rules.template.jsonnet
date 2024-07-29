local kp = (import 'kube-prometheus/main.libsonnet') + 
  (import 'github.com/thanos-io/thanos/mixin/mixin.libsonnet') +
  (import 'kube-prometheus/addons/strip-limits.libsonnet') + {
  values+:: {
    common+: {
      namespace: 'monitoring',
    },
    hostNetworkInterfaceSelector: 'device!~"docker0|virbr0.*|cali.*|lo|tunl0"',
    prometheus+:: {
      replicas: 1,
    },
    kubePrometheus+: {
      platform: 'kubeadm',
    },
    alertmanager+: {
      config: |||
        global:
          resolve_timeout: 10m
        route:
          group_by: ['job']
          group_wait: 30s
          group_interval: 5m
          repeat_interval: 12h
          receiver: 'null'
          routes:
          - match:
              severity: critical
            receiver: 'matrix'
            routes:
            - match_re: # Deprecated
                namespace: "osggpus|osgcpus|osg-services|osg|osg-icecube|osg-opportunistic|cms-ucsd-t2"
              receiver: 'null'
            - match:
                alertname: "KubePersistentVolumeInodesFillingUp"
              receiver: 'null'
          - match:
              alertname: DeadMansSwitch
            receiver: 'null'
        receivers:
        - name: 'null'
        - name: 'matrix'
          webhook_configs:
          - send_resolved: false
            url: $MATRIX_WEBHOOK_URL
     |||,
    },
    grafana+: {
      folderDashboards+:: {
        Ceph: {
          'ceph-cluster.json': (import 'local/grafana/dashboards/Ceph-Cluster.json'),
          'ceph-mds-caps.json': (import 'local/grafana/dashboards/Ceph-MDS-caps.json'),
          'ceph-osds.json': (import 'local/grafana/dashboards/Ceph-OSDs.json'),
          'ceph-pools.json': (import 'local/grafana/dashboards/Ceph-Pools.json'),
          'ceph-rbd.json': (import 'local/grafana/dashboards/Ceph-RBD.json'),
          'ceph-s3.json': (import 'local/grafana/dashboards/Ceph-S3.json'),
          'ceph-recovery.json': (import 'local/grafana/dashboards/Ceph-Recovery.json'),
          'ceph-capacity.json': (import 'local/grafana/dashboards/Ceph-Capacity.json'),
          'volumes.json': (import 'local/grafana/dashboards/Volumes.json'),
        },
        Hardware: {
          'ipmi.json': (import 'local/grafana/dashboards/ipmi.json'),
          'nodediskuse.json': (import 'local/grafana/dashboards/Node-Disk-Usage.json'),
          'node-exporter.json': (import 'local/grafana/dashboards/Node-Exporter.json'),
          'smartctl-temp.json': (import 'local/grafana/dashboards/Smartctl-drive-temp.json'),
        },
        Storage: {
          'seaweedfs.json': (import 'local/grafana/dashboards/Seaweedfs.json'),
          'linstor.json': (import 'local/grafana/dashboards/Linstor.json'),
        },
        Apps: {
          'yunikorn.json': (import 'local/grafana/dashboards/yunikorn.json'),
          'matrix.json': (import 'local/grafana/dashboards/Matrix.json'),
          'kubevirt.json': (import 'local/grafana/dashboards/kubevirt.json'),
          'vllm.json': (import 'local/grafana/dashboards/VLLM.json'),
          'osg-shoveler.json': (import 'local/grafana/dashboards/OSG-Shoveler.json'),
        },
        GPU: {
          'gpu-cluster.json': (import 'local/grafana/dashboards/GPU-Cluster.json'),
          'gpu-cluster-a100.json': (import 'local/grafana/dashboards/GPU-Cluster-A100.json'),
          'gpu-cluster-old.json': (import 'local/grafana/dashboards/GPU-Cluster-Old.json'),
          'gpu-namespace.json': (import 'local/grafana/dashboards/GPU-Namespace.json'),
          'k8snvidiagpu-cluster.json': (import 'local/grafana/dashboards/K8SNvidiaGPU-Cluster.json'),
          'k8snvidiagpu-node.json': (import 'local/grafana/dashboards/K8SNvidiaGPU-Node.json'),
          'k8snvidiagpu-cool.json': (import 'local/grafana/dashboards/GPU-cooling.json'),
        },
        TIDE: {
          'tide-gpu-cpu-utilization-metrics.json': (import 'local/grafana/dashboards/TIDE-GPU-CPU-Utilization-Metrics.json'),
        },
      },
      dashboards+:: {
        'coredns.json': (import 'local/grafana/dashboards/CoreDNS.json'),
        'cpu-namespaces.json': (import 'local/grafana/dashboards/CPU-namespaces.json'),
        'haproxy.json': (import 'local/grafana/dashboards/HAproxy.json'),
        'utilization.json': (import 'local/grafana/dashboards/Utilization.json'),
        'requests.json': (import 'local/grafana/dashboards/requests.json'),
        'cluster-usage.json': (import 'local/grafana/dashboards/Cluster-usage.json'),
        'cluster-usage-nrp.json': (import 'local/grafana/dashboards/Cluster-usage-NRP.json'),
        'workload-total.json': (import 'local/grafana/dashboards/workload-total.json'),
        'pod-total.json': (import 'local/grafana/dashboards/pod-total.json'),
        'namespace-by-pod.json': (import 'local/grafana/dashboards/namespace-by-pod.json'),
        'namespace-by-workload.json': (import 'local/grafana/dashboards/namespace-by-workload.json'),
        'node-map.json': (import 'local/grafana/dashboards/node-map.json'),
      },
      datasources+: [{
        name: 'thanos',
        type: 'prometheus',
        access: 'proxy',
        orgId: 1,
        isDefault: true,
        url: 'http://thanos-querier.monitoring.svc:9090',
        version: 1,
        editable: false,
      },
      {
        "access": "proxy",
        "basicAuth": true,
        "database": "nodes-0",
        "isDefault": false,
        "jsonData": {
            "esVersion": "7.10.0",
            "includeFrozen": false,
            "logLevelField": "",
            "logMessageField": "",
            "maxConcurrentShardRequests": 5,
            "timeField": "timestamp",
            "tlsSkipVerify": true
        },
        "basicAuthUser": "prp",
        "secureJsonData": {
          "basicAuthPassword": "nautilus"
        },
        "name": "Elasticsearch",
        "orgId": 1,
        "readOnly": false,
        "type": "elasticsearch",
        "typeName": "Elasticsearch",
        "uid": "MKTR8nTnz",
        "url": "https://elasticsearch-es-http.igrok-elastic:9200",
      }],      
      config: {
        sections: {
          "auth.anonymous": {enabled: true},
          "security": {admin_password: "$GRAFANA_ADMIN_PASSWORD", allow_embedding: true},
        },
      },
      container: {
        limits: {
          cpu: "2",
          memory: "10Gi",
        },
        requests: {
          cpu: "1",
          memory: "1Gi",
        },
      },
    },
  },
  alertmanager+: {
    alertmanager+: {
      spec+: {
        resources: {
          requests: {
            memory: '100Mi',
            cpu: '10m',
          },
          limits: {
            memory: '500Mi',
            cpu: '1',
          },
        },
      },
    },
    ingress: {
      apiVersion: 'networking.k8s.io/v1',
      kind: 'Ingress',
      metadata: {
        annotations: {
          'kubernetes.io/ingress.class': 'haproxy'
        },
        name: 'alertmanager-nrp',
        namespace: 'monitoring',
      },
      spec: {
        rules: [{
          host: 'alertmanager.nrp-nautilus.io',
          http: {
            paths: [{
              backend: {
                service: {
                  name: 'alertmanager-main',
                  port: {
                    number: 9093
                  }
                },
              },
              path: '/',
              pathType: 'ImplementationSpecific'
            }]
          }
        }],
        tls: [{
          hosts: ['alertmanager.nrp-nautilus.io']
        }]
      }
    }
  },
  kubeStateMetrics+: {
    _config+: {
      scrapeTimeout: '60s',
      scrapeInterval: '60s',
      resources: {
        requests: {
          memory: '1Gi',
          cpu: '1',
        },
        limits: {
          memory: '3Gi',
          cpu: '6',
        },
      },
    },
  },
  prometheus+: {
    prometheus+: {
      spec+: {
        resources: {
          requests: {
            memory: '200Gi',
            cpu: '20',
          },
          limits: {
            memory: '200Gi',
            cpu: '30',
          },
        },
        retention: '168h',
        storage: {
          volumeClaimTemplate: {
            metadata: {
              name: 'vol',
            },
            spec: {
              storageClassName: 'rook-ceph-block-central',
              accessModes: ["ReadWriteOnce"],
              resources: {
                requests: {
                  storage: '3Ti',
                },
              },
            },
          },
        },
        thanos: {
          version: '0.31.0',
          image: 'quay.io/thanos/thanos:v0.31.0',
          objectStorageConfig: {
            key: 'thanos.yaml',
            name: 'thanos-objectstorage',
          },
        },
      },
    },
  },
  prometheusRules: {
    alertRules: {
      apiVersion: 'monitoring.coreos.com/v1',
      kind: 'PrometheusRule',
      metadata: {
        name: 'custom-alert',
        namespace: $.values.common.namespace,
        labels: {
          "app.kubernetes.io/component": "prometheus",
          "app.kubernetes.io/name": "prometheus",
          "app.kubernetes.io/part-of": "kube-prometheus",
          "app.kubernetes.io/version": "2.45.0",
          "prometheus": "k8s",
          "role": "alert-rules",
        },
      },
      spec: {
        groups: [
          {
            name: 'custom.rules',
            rules: [
              (import 'local/prometheus/alerting-rules/ceph-mgr-not-running.json'),
              (import 'local/prometheus/alerting-rules/high-resource-usage.json'),
              (import 'local/prometheus/alerting-rules/osd-out.json'),
              (import 'local/prometheus/alerting-rules/pod-creating.json'),
              (import 'local/prometheus/alerting-rules/pod-terminating.json'),
              (import 'local/prometheus/alerting-rules/volume-attachment-no-pod.json'),
              (import 'local/prometheus/alerting-rules/volume-attachment-no-pvc.json')
            ],
          }
        ]
      }
    },
    recordingRules: {
      apiVersion: 'monitoring.coreos.com/v1',
      kind: 'PrometheusRule',
      metadata: {
        name: 'req-rules',
        namespace: $.values.common.namespace,
        labels: {
          "app.kubernetes.io/component": "prometheus",
          "app.kubernetes.io/name": "prometheus",
          "app.kubernetes.io/part-of": "kube-prometheus",
          "app.kubernetes.io/version": "2.45.0",
          "prometheus": "k8s",
          "role": "alert-rules",
        },
      },
      spec: {
        groups: [
          {
            name: 'req.rules',
            rules: [
              {
                record: 'namespace_gpu_usage',
                expr: |||
                  count (DCGM_FI_DEV_GPU_TEMP) by (namespace)
                ||| % $.values,
              },
              {
                record: 'namespace_gpu_utilization',
                expr: |||
                  sum(DCGM_FI_DEV_GPU_UTIL) by (namespace) / count (DCGM_FI_DEV_GPU_UTIL) by (namespace)
                ||| % $.values,
              },
              {
                record: 'namespace_cpu_utilization',
                expr: |||
                  sum(node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate* on(namespace, pod) group_left kube_pod_status_phase{phase = "Running"}) by (namespace) / sum(kube_pod_container_resource_requests{resource="cpu"}* on(namespace, pod) group_left kube_pod_status_phase{phase = "Running"}) by (namespace)
                ||| % $.values,
              },
              {
                record: 'namespace_cpu_usage',
                expr: |||
                  sum(node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate* on(namespace, pod) group_left kube_pod_status_phase{phase = "Running"}) by (namespace)
                ||| % $.values,
              },
              {
                record: 'namespace_memory_utilization',
                expr: |||
                  sum( container_memory_rss{container!=""} * on(namespace, pod) group_left kube_pod_status_phase{phase = "Running"}) by (namespace) / sum( kube_pod_container_resource_requests{resource="memory"} * on(namespace, pod) group_left kube_pod_status_phase{phase = "Running"}) by (namespace)
                ||| % $.values,
              },
              {
                record: 'namespace_memory_usage',
                expr: |||
                  sum( container_memory_rss{container!=""} * on(namespace, pod) group_left kube_pod_status_phase{phase = "Running"}) by (namespace)
                ||| % $.values,
              },
              {
                record: 'namespace_used_resources',
                expr: |||
                  sum by(namespace, node, resource) ((label_replace(label_replace(sum(DCGM_FI_DEV_GPU_UTIL/100) by (namespace, Hostname, pod), "node", "$1", "Hostname", "(.*)"), "resource", "nvidia_com_gpu", "", "") or label_replace(sum by (node, namespace, pod) (node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate), "resource", "cpu", "", "") or label_replace(sum by (node, namespace, pod) (container_memory_rss{container!=""}), "resource", "memory", "", "")) * on(namespace, pod) group_left kube_pod_status_phase{phase = "Running"}) > 0
                ||| % $.values,
              },
              {
                record: 'namespace_allocated_resources',
                expr: |||
                  sum by (namespace, node, resource) (kube_pod_container_resource_requests * on (namespace, pod) group_left kube_pod_status_phase{phase='Running'}) > 0
                ||| % $.values,
              }
            ],
          }
        ]
      }
    }
  },
  rgw: {
    serviceMonitor: {
      "apiVersion": "monitoring.coreos.com/v1",
      "kind": "ServiceMonitor",
      "metadata": {
        "name": "rgw-mon",
        "namespace": "monitoring",
        "labels": {
          "k8s-app": "rgw-mon"
        }
      },
      "spec": {
        "selector": {
          "matchLabels": {
            "k8s-app": "rgw-mon"
          }
        },
        "namespaceSelector": {
          "matchNames": [
            "rook"
          ]
        },
        "endpoints": [
          {
            "port": "exporter",
            "path": "/metrics"
          }
        ]
      }
    }
  },
  ipmi: {
    serviceMonitor: {
       "apiVersion": "monitoring.coreos.com/v1",
       "kind": "ServiceMonitor",
       "metadata": {
          "name": "ipmi-mon",
          "namespace": "monitoring",
          "labels": {
            "k8s-app": "ipmi-mon"
          }
       },
       "spec": {
          "selector": {
             "matchLabels": {
              "k8s-app": "ipmi-mon"
             }
          },
          "namespaceSelector": {
             "matchNames": [
                "ipmi"
             ]
          },
          "endpoints": [
            {
              "port": "exporter",
              "path": "/metrics"
            }
          ]
       }
    }
  },
};

{ ['00namespace-' + name]: kp.kubePrometheus[name] for name in std.objectFields(kp.kubePrometheus) } +
{ ['0prometheus-operator-' + name]: kp.prometheusOperator[name] for name in std.objectFields(kp.prometheusOperator) } +
{ ['alertmanager-' + name]: kp.alertmanager[name] for name in std.objectFields(kp.alertmanager) } +
{ ['grafana-' + name]: kp.grafana[name] for name in std.objectFields(kp.grafana) } +
{ ['ipmi-' + name]: kp.ipmi[name] for name in std.objectFields(kp.ipmi) } +
{ ['kube-state-metrics-' + name]: kp.kubeStateMetrics[name] for name in std.objectFields(kp.kubeStateMetrics) } +
{ ['kubernetes-' + name]: kp.kubernetesControlPlane[name] for name in std.objectFields(kp.kubernetesControlPlane) } +
{ ['node-exporter-' + name]: kp.nodeExporter[name] for name in std.objectFields(kp.nodeExporter) } +
{ ['prometheus-' + name]: kp.prometheus[name] for name in std.objectFields(kp.prometheus) } +
{ ['prometheus-rules-' + name]: kp.prometheusRules[name] for name in std.objectFields(kp.prometheusRules) } +
{ ['prometheus-adapter-' + name]: kp.prometheusAdapter[name] for name in std.objectFields(kp.prometheusAdapter) } +
{ ['rgw-' + name]: kp.rgw[name] for name in std.objectFields(kp.rgw) }

