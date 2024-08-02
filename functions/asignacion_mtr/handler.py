import sys, os, importlib
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta

sys.path.append("libs")
from ammper.pg8000 import Pg8000
from ammper.aws import AwsSession
my_session = AwsSession()

STAGE = os.environ.get('STAGE', 'local')
ARN_RDS_SECRET_MANAGER_ROLE = os.environ.get('ARN_RDS_SECRET_MANAGER_ROLE', 'arn:aws:iam::381492027664:role/mshabes_access_secret_data_from_pci_prod_role')
RDS_SECRET_ID = os.environ.get('RDS_SECRET_ID', 'mshabes_rds_access_data_from_pci_prod')

if STAGE != 'local':
  from oferta_mtr.func import soap_request, save_to_db
else:
  from func import soap_request, save_to_db

def handler(event = None, context = None):
  global db_instance
  print(event)
  if "id_pci" not in event:
    raise Exception("id_pci es requerido")
  start_date = dt.now() - relativedelta(days=5)
  end_date = dt.now() - relativedelta(days=1)
  if "start_date" in event:
     start_date = dt.strptime(event['start_date'], '%Y-%m-%d')
  if "end_date" in event:
     end_date = dt.strptime(event['end_date'], '%Y-%m-%d')
  try:
    credentials_rds = my_session.get_credentials_rds_from_secret_manager(arn_role=ARN_RDS_SECRET_MANAGER_ROLE, secret_id=RDS_SECRET_ID)
    db_instance = Pg8000(credentials_rds, is_secret_manager=True)
    try:
      # Process for cargas agregadas
      df = soap_request(client=event, start_date=start_date, end_date=end_date)
      if df is not None and len(df) > 0:
        save_to_db(db_instance=db_instance, client=event, df=df)
      status_code = 200
      message = "OK"
      response_data = {}
    except Exception as e:
      print(f"Error al enviar a PCI: {e}")
      response_data = {}
      status_code = 500
      message = str(f"Error al enviar a PCI: {e}")
    finally:
      db_instance.close()
  except Exception as e:
    print(f"Error al conectar con la base de datos: {e}")
    status_code = 500
    message = "Error al conectar con la base de datos"
    response_data = {}

  return {
    "statusCode": status_code,
    "messageResponse": message,
    "responseContent": response_data,
  }

if __name__ == '__main__':
  handler({
  "id_pci": "MEXSOLARGTO_I",
  "asset_id": "CAMX1"
})