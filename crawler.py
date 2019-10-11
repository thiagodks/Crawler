from PyPDF2 import PdfFileReader
from bs4 import BeautifulSoup
from pdf2jpg import pdf2jpg
from pathlib import Path
from PIL import Image
import requests
import PyPDF2
import re
import os

def edit(link):
	link = link[9:]
	cont = 0
	for ch in link:
		if ch != '"': cont+=1
		else: break

	link = link[:cont]
	return link

def editLinks(links):
	newLinks = []
	link = str(links[0])
	newLinks.append(edit(link))
	link = str(links[1])
	newLinks.append(edit(link))
	return newLinks

# Obtem todos os links das provas e dos gabaritos de todos os anos/cursos
# Retorna um dicionário do tipo: Ano -> Área -> Link Prova -> Link Gabarito
def getData(page_link):

	page = requests.get(page_link)

	soup = BeautifulSoup(page.text, 'html.parser')
	pageAll = soup.find_all(class_='list-download--three-columns filter-item')

	anos = 2017
	dicEnade = {}

	for pg1 in pageAll:
			
		dicEnade[anos] = {}

		for pg2 in pg1:

			if pg2 == '\n':	continue
		
			area = str(pg2.find('h6'))
			area = area.replace ("<h6>", "")
			area = area.replace ("</h6>", "")

			links = pg2.find_all('a', attrs={'href': re.compile("^http://")})

			if len(links) == 0: continue
			
			links = editLinks(links)

			dicEnade[anos][area] = {}
			dicEnade[anos][area][links[0]] = links[1]

		anos-=1

	return dicEnade

# Salva um arquivo PDF
def savePdf(diretorio, link, nomeArq):

	filename = Path(diretorio+nomeArq)
	url = link
	response = requests.get(url)
	filename.write_bytes(response.content)

# Faz o Download de todos os PDF's
def DownloadPG(dicEnade):

	for ano in dicEnade:

		os.mkdir('EnadeProvas/'+str(ano))
		print(">> Ano: ", ano)

		for area in dicEnade[ano]:
			
			os.mkdir('EnadeProvas/'+str(ano)+'/'+area)
			print("  >> Área: ", area)
			
			for linkp in dicEnade[ano][area]:
				
				print("     Downloading -> Prova: ", linkp)
				print("     Downloading -> Gabarito: ", dicEnade[ano][area][linkp])
				input("")
				savePdf('EnadeProvas/'+str(ano)+'/'+area+'/', linkp, 'Prova.pdf')
				savePdf('EnadeProvas/'+str(ano)+'/'+area+'/', dicEnade[ano][area][linkp], 'Gabarito.pdf')
				
		print("\n")


# Salva o dicionário com todas as informações
def saveDic(dicEnade):

	arqDic = open('dicEnade.txt', 'w')

	for ano in dicEnade:

		print(">> Ano: ", ano)

		for area in dicEnade[ano]:
			
			print("  >> Área: ", area)
			arqDic.write(str(ano)+'::'+str(area)+'\n')

	arqDic.close()

if __name__ == '__main__':

	dicEnade = {}
	# Obtêm os links de download
	dicEnade = getData('http://portal.inep.gov.br/educacao-superior/enade/provas-e-gabaritos')
	# Faz o download das provas e gabaritos
	DownloadPG(dicEnade)
	# Salva o dicionário
	saveDic(dicEnade)