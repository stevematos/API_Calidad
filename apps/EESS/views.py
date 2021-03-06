import json

from django.db import  connection
from django.shortcuts import render
from rest_framework import status,generics
from rest_framework.response import Response
from Algoritmos.algoritmos_bd import dictfetchall
from apps.datos_metricas.models import MesesYear, Resultados, Indicador, Atributo
from rest_framework.views import APIView
from apps.EESS.models import Eess, Anotaciones
from apps.EESS.serializers import EessSerializer

# Create your views here.
from apps.datos_metricas.serializers import ResultadoSerializer


class EESSList(APIView):
    serializer=EessSerializer
    def get(self,request,iddiris):
        eess=Eess.objects.all().filter(diris_iddiris=iddiris)
        response=self.serializer(eess,many=True)
        print(response.data)
        return Response(response.data)


class EESSMetricaColor(APIView):
    serializer=EessSerializer
    def get(self,request,iddiris,metrica,color=''):
        #metrica=1
        valores=[metrica,iddiris]
        """atributo=Atributo.objects.get(idindicador=metrica, atributo="pct")
        MesYear=MesesYear.objects.all().order_by('-idfecha')[0]
        if color != '' :
            resultado=Resultados.objects.filter(ideess__diris_iddiris_id=iddiris,color=color,idfecha=MesYear.idfecha,idatributo=atributo.idatributo)
        else:
            resultado =Resultados.objects.filter(ideess__diris_iddiris_id=iddiris,idfecha=MesYear.idfecha,idatributo=atributo.idatributo)
        response=[]
        for resul in resultado:
            eess=Eess.objects.get(ideess=resul.ideess.ideess)
            json=(self.serializer(eess)).data
            json['color']=resul.color
            json['porcentaje']=resul.porcentaje
            response.append(json)"""
        sql="""select e.*,r.color,r.porcentaje from eess e
              join resultados r on  e.idEESS=r.idEESS
              where r.idatributo=(
                select atri.idatributo from atributo atri where atri.idindicador=(%s) and atri.atributo='pct'
              ) and r.idfecha = (select idfecha from `meses-year` order by idfecha desc limit 1)
              and e.diris_iddiris=(%s)"""
        if color!='':
            sql=sql+"and  r.color='"+color+"'"
        cursor=connection.cursor()
        cursor.execute(sql,valores)
        datos=dictfetchall(cursor)
        cursor.close()
        return Response(datos)

class EESSgetRenaes(APIView):
    serializerEess= EessSerializer
    serializerResultado =ResultadoSerializer
    def get(self,request,renaes,iddiris):
        """try:
            eess=Eess.objects.get(renaes=renaes,diris_iddiris_id=iddiris)
        except Eess.DoesNotExist:
            return Response('NO EXISTE EL CENTRO DE SALUD',status=status.HTTP_400_BAD_REQUEST)
        MesYear = MesesYear.objects.all().order_by('-idfecha')[0]
        resultados=Resultados.objects.filter(ideess=eess.ideess,idfecha=MesYear.idfecha)
        resultadoResponse = (self.serializerResultado(resultados,many=True)).data
        response=(self.serializerEess(eess)).data
        response['metricas']=resultadoResponse"""
        datos=[renaes,iddiris]
        sql="""select e.*,p.color,p.porcentaje from eess e
                    join promedio p on e.idEESS=p.idEESS
                    where p.idfecha=(select idfecha from `meses-year` order by idfecha desc limit 1)
                    and e.renaes=(%s) and e.diris_iddiris=(%s)"""
        sql2 = """select i.idindicador,r.color,i.nombre,r.porcentaje,r.idfecha from resultados r
                join atributo a on r.idatributo=a.idatributo
                join indicador i on a.idindicador = i.idindicador
                where r.idfecha=
                     (select idfecha from `meses-year` order by idfecha desc limit 1)
                     and r.idEESS=(%s)"""
        cursor=connection.cursor()
        cursor.execute(sql,datos)
        response=dictfetchall(cursor)
        datos2=[(response[0])['idEESS']]
        cursor.execute(sql2,datos2)
        response[0]['metricas']=dictfetchall(cursor)

        return Response(response[0],status=status.HTTP_200_OK)

class EESSgetNombre(APIView):
    serializerEess= EessSerializer
    serializerResultado =ResultadoSerializer
    def get(self,request,nombre,iddiris):
        """try:
            eess=Eess.objects.get(nombre=nombre,diris_iddiris_id=iddiris)
        except Eess.DoesNotExist:
            return Response('NO EXISTE EL CENTRO DE SALUD',status=status.HTTP_400_BAD_REQUEST)
        MesYear = MesesYear.objects.all().order_by('-idfecha')[0]
        resultados=Resultados.objects.filter(ideess=eess.ideess,idfecha=MesYear.idfecha)
        resultadoResponse = (self.serializerResultado(resultados,many=True)).data
        response=(self.serializerEess(eess)).data
        response['metricas']=resultadoResponse"""
        datos=[nombre,iddiris]
        sql="""select e.*,p.color,p.porcentaje from eess e
                    join promedio p on e.idEESS=p.idEESS
                    where p.idfecha=(select idfecha from `meses-year` order by idfecha desc limit 1)
                    and e.nombre=(%s) and e.diris_iddiris=(%s)"""
        sql2 = """select i.idindicador,r.color,i.nombre,r.porcentaje,r.idfecha from resultados r
                join atributo a on r.idatributo=a.idatributo
                join indicador i on a.idindicador = i.idindicador
                where r.idfecha=
                     (select idfecha from `meses-year` order by idfecha desc limit 1)
                     and r.idEESS=(%s)"""
        cursor=connection.cursor()
        cursor.execute(sql,datos)
        response=dictfetchall(cursor)
        datos2=[(response[0])['idEESS']]
        cursor.execute(sql2,datos2)
        response[0]['metricas']=dictfetchall(cursor)

        return Response(response[0],status=status.HTTP_200_OK)

class EessNotas(APIView):
    def get(self,request,ideess,idfecha):
        cursor=connection.cursor()
        sql="""select anotacion,titulo,contenido,estado 
                              from anotaciones
                              where fecha=(%s) and EESS_idEESS=(%s)"""
        cursor.execute(sql,[idfecha,ideess])
        response=dictfetchall(cursor)
        cursor.close()
        return Response(response,status=status.HTTP_200_OK)

    def post(self,request,ideess,idfecha):
        data=request.data
        cursor = connection.cursor()

        sql="""delete from anotaciones where EESS_idEESS=(%s) and fecha=(%s)"""
        cursor.execute(sql,[ideess,idfecha])
        values=[]
        fecha = idfecha
        id_diris = ideess
        estado = True
        for datos in data:
            titulo=datos['titulo']
            anotacion=datos['anotacion']
            contenido=datos['contenido']
            value=[anotacion, titulo, json.dumps(contenido), estado, fecha, id_diris]
            #print(contenido)
            values.append(value)

        cursor.executemany('insert into anotaciones(anotacion, titulo, contenido, estado, fecha, EESS_idEESS) values (%s,%s,%s,%s,%s,%s)', values)
        cursor.close()
        print('Completado')
        return Response('INGRESO DE ANOTACIONES CON EXITO', status=status.HTTP_200_OK)

class EESSMetricasColorFecha(APIView):
    def get(self,request,ideess,idfecha):
        sql="""select i.idindicador,r.color,i.nombre,r.porcentaje,r.idfecha from resultados r
                join atributo a on r.idatributo=a.idatributo
                join indicador i on a.idindicador = i.idindicador
                where r.idfecha=(%s)
                     and r.idEESS=(%s)"""
        cursor=connection.cursor()
        cursor.execute(sql,[idfecha,ideess])
        response=dictfetchall(cursor)
        return Response(response,status=status.HTTP_200_OK)

class EessPromedioColor(APIView):
    def get(self,request,iddiris,color=""):
        sql=""
        datos=[]
        datos.append(iddiris)
        sql="""select e.*,p.color,p.porcentaje from promedio p
               join eess e on p.idEESS=e.idEESS
               where e.diris_iddiris=(%s) and p.idfecha= (select idfecha from `meses-year` order by idfecha desc limit 1)"""
        if color!="":
            sql=sql+"and color=(%s)"
            datos.append(color)
        cursor = connection.cursor()
        cursor.execute(sql, datos)
        response=dictfetchall(cursor)
        cursor.close()
        return Response(response,status=status.HTTP_200_OK)

class EessFechaColor(APIView):
    def get (self,request,ideess,idfecha):
        datos=[ideess,idfecha]
        sql="""select color,porcentaje from promedio where idEESS=(%s) and idfecha=(%s)"""
        cursor = connection.cursor()
        cursor.execute(sql, datos)
        response=dictfetchall(cursor)
        return Response(response[0],status=status.HTTP_200_OK)
