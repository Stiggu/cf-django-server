from .models import Rates, Contracts
from .serializers import ContractSerializer, SaveSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser

import base64
import io
import pandas as pd


def save_contracts(contract) -> Contracts:
    """
    Revisa la data de un JSON y la agrega a la base de datos.
    :param contract: Data del request
    :return: Devuelve un contrato.
    """

    name = contract['name']
    date = contract['date']

    contract_data = Contracts(
        name=name,
        date=date,
    )
    contract_data.save()

    return contract_data


def decode_file(codified_string) -> io.BytesIO:
    """
    Revisa en String en BASE64 y lo decodifica, luego lo vuelve un objeto BytesIO
    :param codified_string:
    :return: Devuelve el objeto BytesIO
    """
    if codified_string.find(',') != -1:
        formatted_data = base64.b64decode(codified_string[codified_string.find('base64,') + 7:])
    else:
        formatted_data = base64.b64decode(codified_string)
    excel = io.BytesIO()
    excel.write(formatted_data)
    excel.seek(0)
    return excel


def save_rates(df: pd.DataFrame, contract: Contracts) -> bool:
    """
    Guarda cada fila del archivo excel (cada Ruta) a un contrato.
    :param df: Dataframe de Pandas
    :param contract: Objecto de Contratos
    :return:
    """
    for index, row in df.iterrows():
        rates_data = Rates(
            contract=contract,
            origin=row['POL'],
            destination=row['POD'],
            currency=row['Curr.'],
            twenty=row["20'GP"],
            forty=row["40'GP"],
            fortyhc=row["40'HC"],
        )
        rates_data.save()

    return True


@api_view(['POST'])
@parser_classes([JSONParser])
def compare(request):
    # Validando la data a la entrada con un Serializador
    request_serializer = SaveSerializer(data=request.data)
    if not request_serializer.is_valid():
        return Response({'errors': request_serializer.errors, 'message': 'Alguno de los campos tiene data erronea.'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Asegurando que sean 2 archivos para la comparacion
    if len(request.data['file']) != 2:
        return Response({'message': 'Deben ser 2 archivos excel para comparar.'}, status=status.HTTP_400_BAD_REQUEST)

    # Decodificando los 2 archivos de Base64
    excel1 = decode_file(request.data['file'][0])
    excel2 = decode_file(request.data['file'][1])

    # Asegurando que sea un archivo excel
    try:
        df1 = pd.read_excel(excel1)
        df2 = pd.read_excel(excel2)
    except ValueError:
        return Response({'message': 'El campo de archivo deberia ser un archivo Excel.'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Creando un Dataframe que va a tener toda la data
    comparer_df = pd.DataFrame({})

    # Moviendo la data al nuevo Dataframe y llenando las casillas vacias
    comparer_df['route1'] = df1['Routing'].fillna('None')
    comparer_df['route2'] = df2['Routing'].fillna('None')

    # Comparando cuales rutas son iguales y convirtiendolas a JSON para el envio al front-end
    comparer_df['check'] = comparer_df['route1'] == comparer_df['route2']
    r = comparer_df.to_json()

    # Respuesta del back-end
    return Response(r, status=status.HTTP_200_OK)


@api_view(['POST'])
@parser_classes([JSONParser])
def save(request):
    # Validando la data a la entrada con un Serializador
    request_serializer = SaveSerializer(data=request.data)
    if not request_serializer.is_valid():
        return Response({'errors': request_serializer.errors, 'message': 'Alguno de los campos tiene data erronea.'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Guardando el contrato a la base de datos
    contract_data = save_contracts(request.data)

    # Revision de cada archivo excel pasado, puede soportar cuantos sean necesarios
    for file in request.data['file']:
        # Decodificando la data del front-end, archivo en Base64
        excel = decode_file(file)

        # Test para saber si es un archivo Excel
        try:
            df = pd.read_excel(excel)
        except ValueError:
            return Response({'message': 'El campo de archivo deberia ser un archivo Excel.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Guardando la data de las rutas a la base de datos
        saved = save_rates(df, contract_data)

        # En caso que falte data en el excel, devuelve un error
        if not saved:
            return Response({'message': 'El archivo Excel le falta data, revisar las columnas.'}, status=status.HTTP_400_BAD_REQUEST)

    # Serializando la respuesta desde la base de datos usando el contrato creado
    serializer = ContractSerializer(contract_data)
    # Respuesta del Backend
    return Response(serializer.data, status=status.HTTP_200_OK)
