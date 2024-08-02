import json, os, sys

STAGE = os.environ.get('STAGE', 'local')
ARN_RDS_SECRET_MANAGER_ROLE = os.environ.get('ARN_RDS_SECRET_MANAGER_ROLE', 'arn:aws:iam::381492027664:role/mshabes_access_secret_nominacion_dev_role')
RDS_SECRET_ID = os.environ.get('RDS_SECRET_ID', 'mshabes_rds_access_nominacion_dev')

if STAGE != 'local':
  sys.path.append("libs")
else:
  sys.path.append("server/libs")

from ammper.aws import AwsSession
from ammper.pg8000 import Pg8000

my_session = AwsSession()

def handler(event = None, context = None):
  print(event)
  ids_pci = []
  try:
    credentials_rds = my_session.get_credentials_rds_from_secret_manager(arn_role=ARN_RDS_SECRET_MANAGER_ROLE, secret_id=RDS_SECRET_ID)
    db_instance = Pg8000(credentials_rds, is_secret_manager=True)
    try:
      ids_pci = db_instance.fetch(f"""SELECT id_pci, asset_id FROM ti_cat_clientes WHERE id_pci IS NOT NULL;""")
      response_data = {}
      status_code = 200
      message = "OK"
    except Exception as e:
      response_data = {}
      status_code = 500
      message = str(f"Error al obtener la información: {e}")
    finally:
      db_instance.close()
  except:
    status_code = 500
    message = "Error al conectar con la base de datos"
    response_data = {}
  
  print({"statusCode": status_code, "body": json.dumps(response_data), "message": message, "ids_pci": ids_pci})
  
  if status_code == 500:
    raise Exception(message)
  
  return ids_pci

if __name__ == "__main__":
  handler({"date": "2023-10"})