def soap_request(client, start_date, end_date):
  import pandas as pd
  from datetime import datetime as dt
  import requests, os, base64, json, ast
  from requests.auth import HTTPBasicAuth
  import xml.etree.ElementTree as ET

  USERNAME_PCI = os.environ.get('USERNAME_PCI', 'ammperservices')
  PASSWORD_PCI = os.environ.get('PASSWORD_PCI', 'Pci_Amm_SRV123!')
  try:
    url = "https://ammper.powercosts.com/axis/services/ScriptLibraryRunRemoteEditor"
    usuario = USERNAME_PCI
    contraseña = PASSWORD_PCI
    headers = {
        "SOAPAction": "",
        "Content-Type": "application/xml",
    }

    payload = """
      <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:edit="http://editor.gtdw.pci.com" >
        <soapenv:Header/>
        <soapenv:Body>
            <edit:run>
              <in0 xsi:type="xsd:string">CST.MX</in0>
                  <in1 xsi:type="xsd:string">new com.ammper.process.external.webservice.GetOffers()</in1>
                  <in2 xsi:type="xsd:string">runJBWS</in2>
                  <in3 xsi:type="scr:ArrayOf_xsd_anyType" xmlns:scr="https://ammper.powercosts.com/axis/services/ScriptLibraryRunRemoteEditor">
                      <json xsi:type="xsd:string">{"beginDate":"%s","endDate":"%s","Client":"%s","edition":"MTR"}</json>
                  </in3>
            </edit:run>
        </soapenv:Body>
      </soapenv:Envelope>
        """ % (f'{start_date.strftime("%d/%m/%Y")}', f'{end_date.strftime("%d/%m/%Y")}', client["id_pci"])
    response = requests.post(url, headers=headers, auth=HTTPBasicAuth(usuario, contraseña), data=payload)
    if response.status_code == 200:
      root = ET.fromstring(response.text)
      run_return = root.find('.//runReturn').text

      if run_return is not None:
        decoded_bytes = base64.b64decode(run_return).decode("utf-8")
        array = json.loads(decoded_bytes)[client["id_pci"]]
        array = ast.literal_eval(ast.literal_eval(array))
        new_array = []
        for i in array:
          value, date_hour = i.split('|')
          date, hour = date_hour.split(' ')
          new_array.append({'mtr': value, 'date': dt.strptime(date, "%m/%d/%Y"), 'hour': int(hour)})
        df = pd.DataFrame(new_array)
        print("Finalizado extracción de datos")
        return df
      return None
    else:
      raise Exception(f"No se encontro informacion para el cliente {client['asset_id']}")
  except Exception as e:
    print(f"Error al consultar la informacion: {e} - {response.text}")
    raise Exception(f"Error al consultar la informacion: {e} - {response.text}")