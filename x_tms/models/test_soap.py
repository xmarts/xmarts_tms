#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- coding: 850 -*-
# -*- coding: ascii -*-

# from suds.client import Client
# import urllib2
# from xml.etree import ElementTree

# url="http://www.gmapserver.com/GlobalMap_API/V3/GlobalMapWSDL.wsdl"
# client = Client(url)
# #print client ## shows the details of this service

# result = client.service.CalcularRuta("225217657648564", 16, 15, 18, 2.5, 4, 0, 0, 1, 1, 1, 3,
# "Monterrey", 0, 0, 1, 2, "Guadalajara", 0, 0, 2, 3, "Morelia", 0, 0, 2, -5, "", 0, 0, 0, 0, "0", 0, 0, 0,
# 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0,
# 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0,
# "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0)
# #print result ## see: restult.txt below
# root = ElementTree.fromstring(result)
# root.write(open('person.xml', 'w'), encoding='utf8')

# root = ET.Element("root")
# doc = ET.SubElement(root, "doc")

# ET.SubElement(docdoc, "field1", name="blah").text = result

# tree = ET.ElementTree(root)
# tree.write("filename.xml")

# from suds.client import Client

# auth_client = Client('http://www.gmapserver.com/GlobalMap_API/V3/GlobalMapWSDL.wsdl')
# request = auth_client.factory.create('ns:GlobalMapSOAP')
# request.login = 'ti@sli.mx'
# request.password = '475957735437301'

# auth_object = auth_client.service.GetAccessToken(request)

# client = Client('http://www.gmapserver.com/GlobalMap_API/V3/GlobalMapWSDL.wsdl')
# client.set_options(soapheaders=auth_object)

# from SOAPpy import WSDL
# from SOAPpy import Types

# # # you can download this and use it locally for better performance
# wsdl = "http://www.gmapserver.com/GlobalMap_API/V3/GlobalMapWSDL.wsdl"
# namespace = "http://web.cbr.ru/"
# input = Types.dateType(name = (namespace, "On_date"))

# proxy = WSDL.Proxy(wsdl, namespace = namespace)
# proxy.soapproxy.config.debug = 1

# proxy.CalcularRuta("225217657648564", 16, 15, 18, 2.5, 4, 0, 0, 1, 1, 1, 3,
# "Monterrey", 0, 0, 1, 2, "Guadalajara", 0, 0, 2, 3, "Morelia", 0, 0, 2, -5, "", 0, 0, 0, 0, "0", 0, 0, 0,
# 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0,
# 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0,
# "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0)

# wsdl = "http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx?wsdl"
# namespace = "http://web.cbr.ru/"
# input = Types.dateType(name = (namespace, "On_date"))

# proxy = WSDL.Proxy(wsdl, namespace = namespace)
# proxy.soapproxy.config.debug = 1

# proxy.GetCursOnDate(input)


from zeep import Client
from xml.etree import ElementTree as ET
import sys
import locale

locale.setlocale(locale.LC_ALL, 'es_MX.UTF-8')

client = Client('http://www.gmapserver.com/GlobalMap_API/V3/GlobalMapWSDL.wsdl')
result = client.service.CalcularRuta("225217657648564", 16, 15, 18, 2.5, 4, 0, 0, 1, 1, 1, 3,
"Monterrey", 0, 0, 1, 2, "Guadalajara", 0, 0, 2, 3, "Morelia", 0, 0, 2, -5, "", 0, 0, 0, 0, "0", 0, 0, 0,
0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0,
0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0,
"", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0, "", 0, 0, 0, 0)
result = result.encode('utf-8')
print result
tree = ET.XML(result)
with open("file.xml", "w") as f:
    f.write(ET.tostring(tree))