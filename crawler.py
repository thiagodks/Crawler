from bs4 import BeautifulSoup
from pathlib import Path
from PIL import Image # Importando o módulo Pillow para abrir a imagem no script
from PyPDF2 import PdfFileReader
from pdf2jpg import pdf2jpg
from tabula import read_pdf
import pytesseract # Módulo para a utilização da tecnologia OCR
import requests
import enade as ed
import re
import os

filters = ['tabela', 'tabelas', 'Gráfico', 'Gráficos', 'Grafico', 'Gráficos']

def getData(page_link):

	page = requests.get(page_link)
	# site = enade.site

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
			
			links = ed.editLinks(links)

			dicEnade[anos][area] = {}
			dicEnade[anos][area][links[0]] = links[1]

		print('Ano: ', anos)
		anos-=1

	# ed.printDic(dicEnade)
	return dicEnade

def savePdf(diretorio, link, nomeArq):

	filename = Path(diretorio+nomeArq)
	url = link
	response = requests.get(url)
	filename.write_bytes(response.content)

def savePG(dicEnade):

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

def convert_PDF_to_JPG(dicEnade):

	inputpath = "output.pdf"
	outputpath = "./"
	result = pdf2jpg.convert_pdf2jpg(inputpath, outputpath, pages="ALL")
	# print(result)


def convert_JPG_to_TEXT(dicEnade):

	pdf = PdfFileReader(open('Prova.pdf','rb'))
	numPages = pdf.getNumPages()
	# print(pdf.getNumPages())
	texto = pytesseract.image_to_string(Image.open('teste.jpg')) 
	print(texto)
	input("")
	
	texto = ''
	for pagina in range(1, numPages):
		# texto += pytesseract.image_to_string(Image.open('Prova.pdf_dir/'+str(pagina)+'_Prova.pdf.jpg')) 
		texto += pytesseract.image_to_string(Image.open('teste.jpg')) 
		# print("Pagina convertida: ", pagina)
		# print(pytesseract.image_to_string(Image.open('Prova.pdf_dir/'+str(pagina)+'_Prova.pdf.jpg'))) # Extraindo o texto da imagem
		# input("Pagina: "+str(pagina))
	# print(texto)

	# input("end")
	return texto
	# print(pytesseract.image_to_string(Image.open('Prova.pdf_dir/3_Prova.pdf.jpg'))) # Extraindo o texto da imagem

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
	dicEnade = getData('http://portal.inep.gov.br/educacao-superior/enade/provas-e-gabaritos')
	saveDic(dicEnade)
	# # savePG(dicEnade)
	# convert_PDF_to_JPG(dicEnade)
	# input("")
	# pdfFULL = convert_JPG_to_TEXT(dicEnade)
	# pdfFULL = ed.pdfFULL
	# end = pdfFULL.find('QUESTIONARIO')
	# if end > 0:	pdfFULL = pdfFULL[:end]


	# bdQuestoes = {}
	# ano = 2017
	# area = 'Arquitetura e Urbanismo'
	# bdQuestoes[ano] = {}
	# bdQuestoes[ano][area] = []

	# startIndex = 0
	# # pdfFULL = pdfFULL.replace('QUESTAO DISCURSIVA', 'ZZZZZZZZ')
	# # print(pdfFULL)
	# while startIndex != -1:

	# 	startIndex = pdfFULL.find('QUESTAO')
	# 	pdfFULL = pdfFULL.replace('QUESTAO', 'ENCONTRADA', 1)
	# 	endIndex = pdfFULL.find('QUESTAO')

	# 	questao = pdfFULL[startIndex:endIndex]
		
	# 	bdQuestoes[ano][area].append(questao)
	# 	print(questao)

	# 	# startIndex = pdfFULL.find('QUESTAO')
	# 	# pdfFULL = pdfFULL.replace('QUESTAO', 'XXXXXXX', 1)
	# 	# endIndex1 = pdfFULL.find('QUESTAO')
	# 	# endIndex2 = pdfFULL.find('ZZZZZZZZ')

	# 	# if (endIndex2 < startIndex and endIndex2 > 0) or (endIndex2 < endIndex1 and endIndex2 > startIndex):
	# 	# 	pdfFULL = pdfFULL.replace('ZZZZZZZZ', 'YYYYYYY', 1)

	# 	# if endIndex1 < endIndex2 or endIndex2 < startIndex:
	# 	# 	questao = pdfFULL[startIndex:endIndex1]
	# 	print("-----------------------------------------------------------------------------------------------------")
	# 	# elif endIndex2 < endIndex1 and endIndex2 > startIndex:
	# 	# 	questao = pdfFULL[startIndex:endIndex2]
	# 	# 	print("2222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222")
		
	# 	# bdQuestoes[ano][area].append(questao)
	# 	# print(questao)
	# 	print("startIndex", startIndex)
	# 	print("endIndex", endIndex)
	# 	input("")
	# 	# print(startIndex, endIndex)
	# 	# input("PROX")



	# print("Numero de questoes fechadas: ", len(bdQuestoes[ano][area]))
	# for i in bdQuestoes[ano][area]:
	# 	print("=========================================================================")
	# 	print(i)
	# 	print("=========================================================================")
	# 	input("")
	# # print(ed.pdfFULL)
	# # ed.printDic(dicEnade)


