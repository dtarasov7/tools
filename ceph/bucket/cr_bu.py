#!/usr/bin/python3
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import boto3
import botocore.exceptions

def create_bucket(endpoint_url, access_key, secret_key, bucket_name, ca_cert):
    """Создает бакет в Ceph S3 с обработкой ошибок"""
    
    session_params = {
        "aws_access_key_id": access_key,
        "aws_secret_access_key": secret_key
    }

    if ca_cert:
        session_params["verify"] = ca_cert

    # Обработка ошибки при создании клиента
    try:
        s3_client = boto3.client("s3", endpoint_url=endpoint_url, **session_params)
    except botocore.exceptions.NoCredentialsError:
        return {"changed": False, "msg": "Ошибка: не указаны учетные данные AWS.", "error": True}
    except botocore.exceptions.PartialCredentialsError:
        return {"changed": False, "msg": "Ошибка: указаны неполные учетные данные AWS.", "error": True}
    except botocore.exceptions.EndpointConnectionError:
        return {"changed": False, "msg": f"Ошибка подключения к {endpoint_url}. Проверьте URL.", "error": True}
    except Exception as e:
        return {"changed": False, "msg": f"Ошибка при создании клиента S3: {str(e)}", "error": True}

    # Попытка создать бакет
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        return {"changed": True, "msg": f"Бакет '{bucket_name}' успешно создан."}
    
    except botocore.exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]

        if error_code == "BucketAlreadyOwnedByYou":
            return {"changed": False, "msg": f"Бакет '{bucket_name}' уже существует и принадлежит вам."}
        elif error_code == "BucketAlreadyExists":
            return {"changed": False, "msg": f"Бакет '{bucket_name}' уже существует и принадлежит другому пользователю."}
        else:
            return {"changed": False, "msg": f"Ошибка при создании бакета: {str(e)}", "error": True}

def main():
    """Основная функция Ansible-модуля"""
    module_args = {
        "endpoint_url": {"type": "str", "required": True},
        "access_key": {"type": "str", "required": True, "no_log": True},
        "secret_key": {"type": "str", "required": True, "no_log": True},
        "bucket_name": {"type": "str", "required": True},
        "ca_cert": {"type": "str", "required": False, "default": None}
    }

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)
    result = create_bucket(
        module.params["endpoint_url"],
        module.params["access_key"],
        module.params["secret_key"],
        module.params["bucket_name"],
        module.params["ca_cert"]
    )

    if "error" in result:
        module.fail_json(msg=result["msg"])
    else:
        module.exit_json(**result)

if __name__ == "__main__":
    main()

# library/ceph_s3_bucket.py
