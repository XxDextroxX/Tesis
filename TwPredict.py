Docu=pd.read_csv("data_streaming.csv", delimiter='|')
Docu2=Docu[Docu['revisado']=='NO']

for elemento in Docu2.values:
    #proceso predictivo------------------------------------- 
    #--removido: 
    ree = EtiquetaEnTexto(EtiquetarModelLSI(elemento[4]))
    print(ree)
    estadoE=ree
    if(estadoE=='no_emergencia'):
      row=[elemento[0], elemento[1], elemento[2], elemento[3], elemento[4],elemento[5], elemento[6],elemento[7],elemento[8], estadoE,"institution_no_identificada"]
    #fin del proceso predictivo-------------------------
    else:
      row=[elemento[0], elemento[1], elemento[2], elemento[3], elemento[4],elemento[5], elemento[6], elemento[7],elemento[8], estadoE,"institution_no_identificada"]    
    with open('data_etiquetada.csv', 'a') as f:
      writer = csv.writer(f, delimiter='|', quoting=csv.QUOTE_MINIMAL)
      writer.writerow(row)

Docu['revisado']='SI'
Docu.to_csv('data_streaming.csv', sep='|',index=False)

