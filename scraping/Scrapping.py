from lxml import html
import requests
import unicodedata
import re
import json
import os
#import logging
#import time
#import csv
#import pandas as pd
import random


############ logging ############

#logger = logging.getLogger("root")
#logger.setLevel(logging.DEBUG)
#ch = logging.StreamHandler()
#ch.setLevel(logging.DEBUG)
#logger.addHandler(ch)



###### CLEANINGS ######

def replacePTChars(s):
	return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))


def replaceAllNonAlfaNum(s,by_what=" "):
	return re.sub('[^A-Za-z0-9]+', by_what, s)
	
# including trailing spaces
def removeAllExtraSpaces(s):
	#return re.sub(' +', ' ',s)
	return " ".join(s.split())


def sanitize(addr):
	temp = addr.lower()	
	temp = replacePTChars(temp)
	temp = replaceAllNonAlfaNum(temp)
	temp = removeAllExtraSpaces(temp)
	return temp
	
	
###################################


class Scrapping():
	
	SERVICES_BASE_URLS = {
		"racius" : 'https://www.racius.com/',
		"codigopostal.ciberforma" : 'https://codigopostal.ciberforma.pt/dir/',
		"portugalio" : 'https://www.portugalio.com/',
		"gescontact" : 'https://www.gescontact.pt/',
		"einforma" : 'https://www.einforma.pt/servlet/app/portal/ENTP/prod/ETIQUETA_EMPRESA/nif/',
		"guiaempresas" : 'https://guiaempresas.universia.pt/',
	}
	


	def __init__(self):
		pass


	def newResult(self):
		result = {}
		result['type'] = None
		result['nome'] = None
		result['nome_legal'] = None
		result['nif'] = None
		result['data_de_inicio'] = None
		result['morada'] = None
		result['localidade'] = None
		result['distrito'] = None
		result['concelho'] = None
		result['freguesia'] = None
		result['codigo_freguesia'] = None
		result['codigo_postal'] = None
		result['forma_juridica'] = None
		result['telefone'] = None
		result['fax'] = None
		result['cae'] = None
		result['site'] = None
		result['latitude'] = None
		result['longitude'] = None
		result['horario'] = None
		result['email'] = None
		result['telemovel'] = None
		result['estado'] = None
		result['status'] = None
		result['url'] = None
		return result

	'''
	def printR(self, result = None):
		if not result:
			return
		logger.info('type: {}'.format(result['type']))
		logger.info('nome: {}'.format(result['nome']))
		logger.info('nome_legal: {}'.format(result['nome_legal']))
		logger.info('nif: {}'.format(result['nif']))
		logger.info('data_de_inicio: {}'.format(result['data_de_inicio']))
		logger.info('morada: {}'.format(result['morada']))
		logger.info('localidade: {}'.format(result['localidade']))
		logger.info('distrito: {}'.format(result['distrito']))
		logger.info('concelho: {}'.format(result['concelho']))
		logger.info('freguesia: {}'.format(result['freguesia']))
		logger.info('codigo_freguesia: {}'.format(result['codigo_freguesia']))
		logger.info('codigo_postal: {}'.format(result['codigo_postal']))
		logger.info('forma_juridica: {}'.format(result['forma_juridica']))
		logger.info('telefone: {}'.format(result['telefone']))
		logger.info('fax: {}'.format(result['fax']))
		logger.info('cae: {}'.format(result['cae']))
		logger.info('site: {}'.format(result['site']))
		logger.info('latitude: {}'.format(result['latitude']))
		logger.info('longitude: {}'.format(result['longitude']))
		logger.info('horario: {}'.format(result['horario']))
		logger.info('email: {}'.format(result['email']))
		logger.info('telemovel: {}'.format(result['telemovel']))
		logger.info('estado: {}'.format(result['estado']))
		logger.info('url: {}'.format(result['url']))
		logger.info('status: {}'.format(result['status']))
	'''


	def parseName(self, nome, dashes=False, lda = True,  splitted = False, propositions=True, unipessoal = True):
		formatted_name = nome.lower()
		formatted_name = formatted_name.replace('.',"")
		if not propositions:
			# remove de,do,des,dos
			to_remove = [' da', ' de ',' do ',' das ', ' des ',' dos ']
			for i in to_remove:
				formatted_name = formatted_name.replace(i," ")
		if splitted:
			formatted_name = formatted_name.split("-")[0]
		if not lda:
			#if (formatted_name).endswith('lda'):
			#	formatted_name = formatted_name[:-3]
			formatted_name = formatted_name.replace('lda'," ")
			formatted_name = formatted_name.replace('limitada'," ")
		if not unipessoal:
			formatted_name = formatted_name.replace('unipessoal'," ")
				
		if dashes:
			formatted_name = sanitize(formatted_name).replace(" ", "-")

		return formatted_name


	# used by einforma
	def format_date(self, date):
		mes,ano = date.split(' ',2)
		mes = sanitize(mes)
		if mes == "janeiro":
			mes = 1
		elif mes == "fevereiro":
			mes = 2
		elif mes == "marco":
			mes = 3
		elif mes == "abril":
			mes = 4
		elif mes == "maio":
			mes = 5
		elif mes == "junho":
			mes = 6
		elif mes == "julho":
			mes = 7
		elif mes == "agosto":
			mes = 8
		elif mes == "setembro":
			mes = 9
		elif mes == "outubro":
			mes = 10
		elif mes == "novembro":
			mes = 11
		elif mes == "dezembro":
			mes = 12
		return "01-" + str(mes) + "-" + ano


	### the services

	def Racius(self, empresa, NIF = None):
		empresa = self.parseName(empresa,dashes=True)
		URL = self.SERVICES_BASE_URLS['racius'] + empresa + '/'
		page = requests.get(URL)
		tree = html.fromstring(page.content)
		
		r = self.newResult()	
		r['url']  = URL
		
		###
		#tree = html.fromstring(qwe)
		###	
		title = tree.xpath('//title/text()')
		if '404' in title[0]:
			r['status'] = "NOT_FOUNDED"
			return r
		
		#saveFile(id_ent, empresa, 'racius', page.content)
		
		data_json = tree.xpath('//script[@type="application/ld+json"]/text()')
		if len(data_json) > 0:
			data = data_json[0]
			data = json.loads(data)
			
			r['type'] = data.get("@type")
			r['nome'] = data.get("name")
			r['nome_legal'] = data.get("legalName")
			r['nif'] = data.get("taxID")
			#r['descricao'] = data.get("description")
			r['data_de_inicio'] = data.get("foundingDate")
			if data.get("address"):
				r['morada'] = data.get("address").get("streetAddress")
				r['localidade'] = data.get("address").get("addressLocality")
				r['codigo_postal'] = data.get("address").get("postalCode")	

			'''
			if "Em Liquidação" in r['nome']:
				r['estado'] = data.get("Em Liquidação")
			'''
			r['estado'] = "EM ACTIVIDADE"
			if len(data_json) > 1:		
				'''
				data = data_json[1]
				data = json.loads(data)
				r['estado'] = data.get("name")	# ex:  Dissolução e Liquidação  => encerrada
				'''
				for e in data_json:
					e = json.loads(e)
					content = e.get("name")
					if content.find("Dissolução e Liquidação") != -1:
						r['estado'] = "ENCERRADA"
						break
					elif content.find("Insolvência") != -1:
						r['estado'] = "EM INSOLVÊNCIA"
						break
					elif content.find("Revitalização") != -1:
						r['estado'] = "EM REVITALIZAÇÃO"
						break
				
				
			data = tree.xpath('//table[@class="table"]/tr/*/text()')		
			
			#juridica_index = data.index("Forma Jurídica")
			juridica_index = data.index("Forma Jurídica") if "Forma Jurídica" in data else None
			if juridica_index:		
				#if juridica_index > 0:
				r['forma_juridica'] = data[juridica_index + 1]

			if r['data_de_inicio'] == "" or r['data_de_inicio'] is None:
				#init_index = data.index("Data Constituição")
				init_index = data.index("Data Constituição") if "Data Constituição" in data else None
				if init_index:
					r['data_de_inicio'] = data[init_index + 1]		
			
			r['status'] = "OK"
			
			return r
			
		return r



	def CodigoPostal_Ciberforma(self, empresa, NIF = None):
		empresa = self.parseName(empresa,dashes=True)
		# no nif => base/dir/0/empresa
		if NIF is None:
			NIF = 0
		URL = self.SERVICES_BASE_URLS['codigopostal.ciberforma'] + str(NIF) + '/' + empresa + '/'	

		page = requests.get(URL)
		
		tree = html.fromstring(page.content)
		#tree = html.fromstring(qwe)
		
		
		r = self.newResult()
		r['url']  = URL
			
		title = tree.xpath('//title/text()')
		if '404' in title[0]:
			r['status'] = "NOT_FOUNDED"
			return r
			
		#saveFile(id_ent, empresa, 'codigopostal.ciberforma', page.content)	
		
		nome = tree.xpath('//span[@class="auto-title left"]/text()')
		if len(nome) > 0:
			r['nome'] = nome[0]	
			
		#telefone = tree.xpath('//span[@class=""]/text()')
		
		###
		temp = tree.xpath('//h4//text()')
		tel = temp.index("Telefone: ") if "Telefone: " in temp else None
		if tel:
			r['telefone'] = temp[tel + 1]

		tel = temp.index("Fax: ") if "Fax: " in temp else None
		if tel:
			r['fax'] = temp[tel + 1]
		
		tel = temp.index("Site: ") if "Site: " in temp else None
		if tel:
			r['site'] = temp[tel + 1]
		
		tel = temp.index("E-Mail: ") if "E-Mail: " in temp else None
		if tel:
			r['email'] = temp[tel + 1]
		###
		'''
		if len(telefone) > 0:
			r['telefone'] = telefone[0]
		if len(telefone) > 1:
			r['fax'] = telefone[1]
		'''
		morada = tree.xpath('//h4[@class=""]/text()')
		if len(morada) > 0:
			r['morada'] = morada[0]
		if len(morada) > 1:
			r['localidade'] = morada[1]
		if len(morada) > 2:
			cp = re.sub('[^0-9-]+', "", morada[2])
			r['codigo_postal'] = cp
		
		d_c_f = tree.xpath('//h6/a/text()')
		if len(d_c_f) > 0:
			r['freguesia'] = d_c_f[0]
		if len(d_c_f) > 1:
			r['concelho'] = (d_c_f[1].split(' ', 1)[1]).split(' ', 1)[1]
		if len(d_c_f) > 2:
			r['distrito'] = (d_c_f[2].split(' ', 1)[1]).split(' ', 1)[1]

		nif = tree.xpath('//div[@class="ads-details-info col-md-10"]/p/text()')
		if len(nif) > 0:
		#	r['nif'] = re.sub('[^0-9]+', "", nif[2].split(': ')[1])
			nif_item = None
			for i in nif:
				if i.find("contribuinte") != -1:# in i:
					nif_item = i
					break
			if nif_item:
				r['nif'] = re.sub('[^0-9]+', "", nif_item.split(': ')[1])
			data = None
			for i in nif:
				if i.find("Constituída") != -1: # in i:
					data = i
					break
			if data:
				r['data_de_inicio'] = data.split('em ')[1]

		cae = tree.xpath('//div[@class="ads-details-info col-md-8"]/*/text()')
		c_f = ""
		cod_cae = ""
		for i in cae:
			if i.find("Código de freguesia") != -1: # in i:
				c_f = i
			if i.find("com o CAE") != -1:# in i:
				cod_cae = i
		if c_f != '':
			r['codigo_freguesia'] = c_f.split(': ')[1]
		if cod_cae != '':
			r['cae'] = cod_cae.split('com o CAE ')[1]	

		'''
		site = tree.xpath('//a[@rel="nofollow" and @target="_blank"]/text()')
		if len(site) > 0:
			r['site'] = site[0]
		'''
		
		r['status'] = "OK"
		
		return r




	def Portugalio(self, empresa, NIF = None):
		empresa = self.parseName(empresa, dashes=True, lda = False, unipessoal=False)
		URL = self.SERVICES_BASE_URLS['portugalio'] + empresa + '/'	
		page = requests.get(URL)	
		tree = html.fromstring(page.content)
		
		r = self.newResult()
		r['url']  = URL
		
		title = tree.xpath('//title/text()')
		if 'Página não encontrada' in title[0]:
			r['status'] = "NOT_FOUNDED"
			return r

		#saveFile(id_ent, empresa, 'portugalio', page.content)

		
		data = tree.xpath('//script[@type="application/ld+json"]/text()')
		if len(data) > 0:
			#data = data[0]
			data = data[0][data[0].find('{"@') : data[0].find('\/"]}')+5]
			data = json.loads(data)		
			
			r['type'] = data.get("@type")
			if data.get("address"):
				r['codigo_postal'] = data.get("address").get("PostalAddress")		
				r['morada'] = data.get("address").get("streetAddress")
				r['localidade'] = data.get("address").get("addressLocality")		
			r['nome'] = data.get("name")
			if data.get("geo"):
				r['latitude'] = data.get("geo").get("latitude")
				r['longitude'] = data.get("geo").get("longitude")
			r['nif'] = data.get("taxID")		
			r['telefone'] = data.get("telephone")
			if r['telefone']:
				if len(r['telefone']) > 0:
					r['telefone'] = (r['telefone'][0]).replace(" ", "")
			r['fax'] = data.get("faxNumber")
			if r['fax']:
				r['fax'] = r['fax'].replace(" ", "")
			
			if data.get("url"):
				if len(data.get("url")) > 1:
					r['site'] = data.get("url")[1]
			
			r['horario'] = data.get("openingHours")
		
		
			nif = tree.xpath('//div[@class="company-flat-inner-content"]/*/b/text()')
			cae = tree.xpath('//div[@class="company-flat-inner-content"]/*/text()')
			
			if nif:
				nif = "".join(nif)
				r['nif'] = re.sub('[^0-9]+', "", nif)
			

			if cae:
				cae = [s for s in cae if " CAE " in s]
				if len(cae) > 0:
					cae = cae[0].split("CAE ")[1]
					cae = cae.split(" ")[0]
					r['cae'] = cae
		
			r['status'] = "OK"

		return r



	def Gescontact(self, empresa, NIF = None):
		empresa = self.parseName(empresa, dashes=True, splitted = True, propositions=False, unipessoal=False, lda=False)
		URL = self.SERVICES_BASE_URLS['gescontact'] + empresa + '/'	
		page = requests.get(URL)	
		tree = html.fromstring(page.content)
		
		r = self.newResult()
		r['url']  = URL
		r['status'] = "NOT_FOUNDED"
		
		data = tree.xpath('//h2[@style="color:#E03F00; text-align:center;"]/text()')
		if len(data) > 0:
			if data[0].find("Por favor, efetue a vali") != -1: # in data[0]:
				return r

		data = tree.xpath('//script[@type="application/ld+json"]/text()')
		if len(data) > 0:
			
			#saveFile(id_ent, empresa, 'gescontact', page.content)
			
			data = data[0]
			data = json.loads(data)
			
			
			
			r['type'] = data.get("@type")
			r['nome'] = data.get("name")
			if data.get("address"):
				r['morada'] = data.get("address").get("streetAddress")
				r['localidade'] = data.get("address").get("addressLocality")
				r['distrito'] = data.get("address").get("addressRegion")
			
				cp = data.get("address").get("postalCode")
				if cp:
					cp = re.sub('[^0-9-]+', "", cp)
					r['codigo_postal'] = cp
			
			
			#r['telefone'] = data.get("telephone")		
			#r['email'] = data.get("email")
			#telefone = tree.xpath('//a[@class="empresa_telefone"]/@href')
			#if len(telefone) > 0:
			#	r['telefone'] = telefone[0].split(':')[1]
			#telemovel = tree.xpath('//a[@class="empresa_telemovel"]/@href')
			#if len(telemovel) > 0:
			#	r['telemovel'] = telemovel[0].split(':')[1]
			#email = tree.xpath('//a[@class="empresa_email"]/@href')
			#if len(email) > 0:
			#	r['email'] = email[0].split(':')[1]	
			#site = tree.xpath('//a[@class="empresa_site"]/@href')
			#if len(site) > 0:
			#	r['site'] = site[0]
			data = tree.xpath('//a[@class="emp_links"]/@title')
			for i in data:
				if len(i) > 0:
					if i[0] == '2':
						r['telefone'] = i
					elif i[0] == '9':
						r['telemovel'] = i
					elif i[0] == 'h' or i[0] == 'w':
						r['site'] = i
					elif '@' in i:
						r['email'] = i
			
			nif = tree.xpath('//input[@name="nif"]/@value')
			if len(nif) > 0:
				r['nif'] = nif[0]

			
			data = tree.xpath('//a[@class="emp_links"]/text()')
			data = [i.replace("\t","").replace("\n","") for i in data]
		
			#concelho_index = data.index('Concelho:')
			concelho_index = data.index("Concelho:") if "Concelho:" in data else None
			if concelho_index:
				r['concelho'] = data[concelho_index + 1]
			
			#freguesia_index = data.index('Freguesia:')
			freguesia_index = data.index("Freguesia:") if "Freguesia:" in data else None
			if freguesia_index:
				r['freguesia'] = data[freguesia_index + 1]
				
			#cae_index = data.index('CAE:')
			cae_index = data.index("CAE:") if "CAE:" in data else None
			if cae_index:
				r['cae'] = data[cae_index + 1]


			data = tree.xpath('//td[@style="padding:9px 0px 0px 0px; vertical-align:top; color:#333; font-size:16px;"]/text()')
			data = [i.replace("\t","").replace("\n","") for i in data]
			matching = [s for s in data if "-" in s]
			if len(matching) > 0:
				r['data_de_inicio'] = matching[0]
			
			r['status'] = "OK"
		
		
		return r



	def Einforma(self, empresa, NIF = None):
		
		r = self.newResult()
		
		if NIF is None:
			return r
		
		URL = self.SERVICES_BASE_URLS['einforma'] + str(NIF)	+ "/"
		r['url']  = URL
		
		page = requests.get(URL)
		
		tree = html.fromstring(page.content)
		
		status = tree.xpath('//p[@class="title01 mt0"]/text()')
		if len(status) > 0:
			if status[0].find("Empresa não encontrada") != -2: # in status[0]):
				r['status'] = "NOT_FOUNDED"
				return r
		
		#saveFile(id_ent, str(NIF), 'einforma', page.content)	
		
		
		
		nome = tree.xpath('//span[@itemprop="name"]/text()')
		if len(nome) > 0:
			r['nome'] = nome[0]
		
		morada = tree.xpath('//span[@itemprop="streetaddress"]/text()')
		if len(morada) > 0:
			r['morada'] = morada[0]
		
		cp = tree.xpath('//span[@itemprop="postalcode"]/text()')
		if len(cp) > 0:
			r['codigo_postal'] = cp[0]
		
		site = tree.xpath('//span[@itemprop="url"]/text()')
		if len(site) > 0:
			r['site'] = site[0]
		
		
		localidade = tree.xpath('//span[@class="locality"]/text()')
		if len(localidade) > 0:
			r['localidade'] = localidade[0]
		
		data_inicio = tree.xpath('//span[@class="type"]/text()')
		if len(data_inicio) > 0:
			r['data_de_inicio'] = self.format_date(data_inicio[0])	# month year

		r['status'] = "OK"

		return r







	def GuiaEmpresas(self, empresa, NIF = None):
		empresa = self.parseName(empresa, dashes=True, propositions=False, lda = False)
		
		URL = self.SERVICES_BASE_URLS['guiaempresas'] + empresa.upper() + ".html"
		page = requests.get(URL, timeout=5)
		
		tree = html.fromstring(page.content)
		#tree = html.fromstring(qwe)
		
		r = self.newResult()
		r['url']  = URL
		
		status = tree.xpath('//p[@class="h1ficha"]/text()')
		if len(status) > 0:
			if status[0].find("existe no Lista de empresas portuguesas") != -1: # in status[0]):
				r['status'] = "NOT_FOUNDED"
				return r
		
		status = tree.xpath('//h1/text()')
		if status and len(status) > 0:
			if '503' in status[0]:
				r['status'] = "NOT_FOUNDED"
				print (r['status'])
				return r

		
		
		#saveFile(id_ent, empresa, 'guiaempresas', page.content)	
		
		
		f_d = tree.xpath('//a[@itemprop="item"]/@href')	
		#print (f_d)
		for i in f_d:
			#print (i)
			if i.find("freguesia") != -1: # in i:
				f = i.split('/')
				r['freguesia'] = f[len(f) - 2]			
			if i.find("concelho") != -1: # in i:
				f = i.split('/')
				r['distrito'] = f[len(f) - 2]
				

		morada = tree.xpath('//span[@class="street-address"]/text()')
		if len(morada) > 0:
			r['morada'] = morada[0]
			cp = re.search('\d{4}(?:[-]\d{3})?', morada[0]).group(0)
			if cp:
				r['codigo_postal'] = cp

		r['status'] = "OK"


		return r
	


	def getData(self, service, current_company, nif):	
		if service == "racius":
			return self.Racius(current_company,nif)
		elif service == "codigopostal.ciberforma":
			return self.CodigoPostal_Ciberforma(current_company,nif)
		elif service == "portugalio":
			return self.Portugalio(current_company,nif)
		elif service == "gescontact":
			return self.Gescontact(current_company,nif)
		elif service == "einforma":
			return self.Einforma(current_company,nif)
		elif service == "guiaempresas":
			return self.GuiaEmpresas(current_company,nif)


	def scrap(self, current_company, nif = None):#, randomize = False):
		#if randomize:
		#	temp = list(self.SERVICES_BASE_URLS.items())			
		#	random.shuffle(temp)
		#	self.SERVICES_BASE_URLS = dict(temp)

		result = self.newResult()
		for service in self.SERVICES_BASE_URLS:
			
			#logger.info("scrapping with > {}".format(service))
			
			try:
				r = self.getData(service, current_company, nif)
					
				cp = result['codigo_postal']
				stat = result['status']
				url = result['url']
				
				# merge the dictionaries
				result = dict((k,v if k in r and r[k] in [None, ''] else r[k]) for k,v in result.items())
				
				# for now only zip code and status require special attention
				# use the most completed one
				if cp and r['codigo_postal']:
					if len(cp) == 8 and len(r['codigo_postal']) < 8:
						result['codigo_postal'] = cp
				if stat != 'NOT_FOUNDED' and r['status'] == 'NOT_FOUNDED':
					result['status'] = stat
				
				if r['url'] and url:
					result['url'] = url + " # " + r['url']
				
				#print (result)
				#print("------------")
			except Exception as e:
				#print ("ERROR - ",e)
				pass
				#raise
			
					
		return result
			


	





#r = getData(row[NAME_COLUMN], row[NIF_COLUMN], row[ID_COLUMN])				



#printR (Racius(1,"Ideias Bring Solutions Lda"))

#printR (Racius("Geração Discreta, Lda"))

#printR (Racius("Amag - Sociedade de Comércio e Representações, Lda"))

#printR (CodigoPostal_Ciberforma(1,"HEMOVIDA Lda", 506036944))

#printR (CodigoPostal_Ciberforma("Restaurante Capa Negra"))

#printR (Portugalio("Dom Digital - Novas Tecnologias de Informação, Lda"))


#printR (Gescontact(1,"Necterra II, Unipessoal Lda."))

#printR (Einforma(503837903))

#print (GuiaEmpresas("Dom Digital - Novas Tecnologias De Informação, Lda"))
