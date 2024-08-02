def save_to_db(db_instance, client, df):
  print("Guardando datos en base de datos")
  for index, row in df.iterrows():
    try:
      db_instance.execute(f"INSERT INTO oferta_mtr (asset_id, id_pci, mtr, date, hour) VALUES ('{client['asset_id']}', '{client['id_pci']}', '{row['mtr']}', '{row['date']}', '{row['hour']}') ON CONFLICT (asset_id, id_pci, date, hour) DO UPDATE SET mtr = '{row['mtr']}', updated_at = now();")
    except Exception as e:
      print(f"ERROR AL INSERTAR: {e}")
      continue
  print("Finalizado guardado de datos")