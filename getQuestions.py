from pathlib import Path
from PIL import Image
from PyPDF2 import PdfFileReader
from pdf2jpg import pdf2jpg
import pdftotext
import pytesseract
import requests
from PIL import Image 
import send_email as se
import shutil
import re
import os
import sys

# Obtêm o texto de uma imagem
def JPG_to_TXT(IMAGEM):
    texto = pytesseract.image_to_string(Image.open(IMAGEM))
    return texto

# Analisa o texto da Imagem, caso haja alguma questão discursiva, essa imagem será descartada
def analisarIMG(IMAGEM):
    texto = pytesseract.image_to_string(Image.open(IMAGEM))
    disc = ['Discursivas', 'Discursiva', 'DISCURSIVAS', 'DISCURSIVA', 'Questionario', 'QUESTIONARIO', 'Questionário', 'QUESTIONÁRIO']
    for wd in disc:
        questao = texto.find(wd)
        if questao != -1: return -1
    
    return 0

# Analisa uma imagem e obtem seu número de questões, e o número de cada questão 
def getQuestao(IMAGEM):
    
    texto = JPG_to_TXT(IMAGEM)
    
    numQuestoes = 0
    lines = []
    questao = 0
    try:
        while questao != -1:

            questao = texto.find('QUESTAO')

            if questao != -1:
                numQuestoes+=1
                aux = texto[questao:]
                aux = aux[:aux.find('\n')]
                aux = aux.split(' ')
                aux = aux[1]
                lines.append(aux)
                texto = texto.replace('QUESTAO', 'OK', 1)


            if questao == -1:

                questao = texto.find('Questao')

                if questao != -1:
                    numQuestoes+=1
                    aux = texto[questao:]
                    aux = aux[:aux.find('\n')]
                    aux = aux.split(' ')
                    aux = aux[1]
                    lines.append(aux)
                    texto = texto.replace('Questao', 'OK', 1)

    except:
        return 0, '-1', lines
    
    questao = texto.find('Area livre')
    if questao != -1:
        return numQuestoes, 'AL', lines
    
  
    return numQuestoes, '-1', lines

# Analisa uma imagem e verifica se ela é dupla ou simples
# Imagem Dupla: é uma imagem que foi dividida ao meio e possui questões em ambas as partes
# Imagem Simples: é uma imagem que não foi dividida ao meio, possui apenas questoes em sequencia
def pgSD(IMAGEM):
    
    im = Image.open(r""+IMAGEM)
    
    width, height = im.size
    print(width, height)
    
    #Left, top, rigth, bottom
    imR = im.crop((0, 300, width/2, height))
    imR.save('img1.jpg')
    
    imR = im.crop((width/2, 300, width, height))
    imR.save('img2.jpg')
    
    img1Q, lx, nq1 = getQuestao('img1.jpg')
    img2Q, lx, nq2 = getQuestao('img2.jpg')
    nq = nq1 + nq2
    print("Número da Questão: ", nq)
    
    if img1Q == 0 and img2Q == 0:
        return 'none', -1, -1, nq
    
    elif img1Q > 0 and img2Q > 0:
        return 'pgD', img1Q, img2Q, nq
    
    elif img1Q > 0 and img2Q == 0:
        return 'pgS', img1Q, img2Q, nq
    
    elif img1Q == 0 and img2Q > 0:
        return 'none', -1, -1, nq
        
    return 'none', -1, -1, nq


# Carrega o dicionário obtido a partir do Crawler
def getDicEnade():
    
    arqDic = open('dicEnade.txt')
    
    dicEnade = {}
    
    for line in arqDic:
        
        values = line.split('::')
        
        ano, area = values[0], values[1]
        area = area.replace('\n', '', 1)
        
        if ano not in dicEnade.keys():
            dicEnade[ano] = []
            
        dicEnade[ano].append(area)
    
    return dicEnade


# Corta uma imagem, quando identifica uma questão
def cropImage(IMAGEM, ID, diretorio):
    
    print('\n\nProcessando pagina: ', IMAGEM)
    
    # Verifica se a imagem não possui questões discursivas
    if analisarIMG(IMAGEM) == -1:
        print("Questao Discursiva...\nProx...")
        return ID, -1
    
    im = Image.open(r""+IMAGEM)
    
    width, height = im.size

    pagina, img1Q, img2Q, nq = pgSD(IMAGEM)
    if pagina == 'none': 
        print('Nenhuma questão encontrada na pagina: ', IMAGEM)
        return ID, -1
    
    print('Pagina: ', pagina, img1Q, img2Q)
    coordenadasIMG = []
    
    # Obtem as informações da pagina, se ela é dupla ou simples    
    if pagina == 'pgS':
        coordenadasIMG.append((0, 300, width, height-250))
        
    elif pagina == 'pgD':
        coordenadasIMG.append((0, 300, width/2, height-250))
        coordenadasIMG.append((width/2, 300, width, height-250))
        
    elif True:
        print ("ERRO AO IDENTIFICAR QUESTOES")
        return ID, -1
    
    getQ = 0
    # Percorre a(s) imagens em busca das coordenas para extrair as questões
    for i in range(len(coordenadasIMG)):
    
        left, top, right, bottom = coordenadasIMG[i][0], coordenadasIMG[i][1], coordenadasIMG[i][2], coordenadasIMG[i][3]
        print(left, top, right, bottom)
        
        saveTOP = saveBT = cont = 0
        if pagina == 'pgS': 
            result, AL, lx = getQuestao(IMAGEM)
            if AL != 'AL':
                saveBT = bottom+50

        x = 400
        # Percorro a imagem na vertical, em busca das coordenadas para extrair a questão
        while x < height-200:

            imR = im.crop((left, top, right, x))
            imR.save('img.jpg')

            #Obtem o topo de onde cortar a questão
            if saveTOP == 0:
                result, AL, lx = getQuestao('img.jpg')
                if result != 0:
                    saveTOP = x
                    x = x + 100
                    top = top + 100

            # Obtem o fim de onde cortar a questão
            elif saveBT == 0:
                result, AL, lx = getQuestao('img.jpg')
                if AL == 'AL': saveBT = x
                if result != 0: saveBT = x

            # Após identificar o topo e fim da qustão, ela é, então, salva, sendo seu nome, o número da questão
            if saveTOP != 0 and saveBT != 0:
                imR = im.crop((left, saveTOP+10, right, saveBT-50))
                imR.save(diretorio+'/'+nq[getQ]+'.jpg')
                ID+=1
                saveTOP = saveBT = 0
                print("1) Get Question "+str(getQ)+" Success :: ", nq[getQ])
                getQ+=1
                if pagina == 'pgS': break
                
            x+=15
            top+=15
            
        if saveTOP != 0 and saveBT == 0:
            imR = im.crop((left, saveTOP-5, right, bottom))
            imR.save(diretorio+'/'+nq[getQ]+'.jpg')
            ID+=1
            saveTOP = saveBT = 0
            print("1) Get Question "+str(getQ)+" Success :: ", nq[getQ])
            getQ+=1


    print('Numero de questoes capturadas: ', getQ)
    print('Total de questoes: ', img1Q+img2Q)
    return ID, 0

def convert_PDF_to_JPG(namePDF, ano, area):

    inputpath = 'EnadeProvas/'+ano+'/'+area+'/'+namePDF
    outputpath = 'EnadeProvas/'+ano+'/'+area+'/'
    result = pdf2jpg.convert_pdf2jpg(inputpath, outputpath, pages="ALL")

# Extrai todas as questões de todas as imagens!
def extractQuestions(dicEnade):

    ID = 0
    se.sendEmail('thiagoadriano2010@gmail.com', 'Extração de Questões', 'Iniciando extração de questões!')

    for ano in dicEnade.keys():

        print('>> Ano: ', ano)

        for area in dicEnade[ano]:

            try:
                os.mkdir('EnadeProvas/'+ano+'/'+area+'/Questoes')
            except FileExistsError:
                shutil.rmtree('EnadeProvas/'+ano+'/'+area+'/Questoes')
                os.mkdir('EnadeProvas/'+ano+'/'+area+'/Questoes')

            pdf = PdfFileReader(open('EnadeProvas/'+ano+'/'+area+'/Prova.pdf','rb'))
            numPages = pdf.getNumPages()
            for i in range(1, numPages):
                try:
                    ID, OK = cropImage('EnadeProvas/'+ano+'/'+area+'/Prova.pdf_dir/'+str(i)+'_Prova.pdf.jpg', ID, 'EnadeProvas/'+ano+'/'+area+'/Questoes')
                    if OK == -1:
                        print('Pagina Ignorada: ', i)
                    elif True: print('Pagina processada com Sucesso!: ', i)
                except:
                    continue

        se.sendEmail('thiagoadriano2010@gmail.com', 'Extração de Questões', 'Todas as questões do ano: '+ano+' foram extraidas com sucesso!')

# Extrai as respostas dos gabaritos
def extractAnswers(dicEnade):

    for ano in dicEnade.keys():

        print('>> Ano: ', ano)

        for area in dicEnade[ano]:

            print('   >> Area: ', area)
            dicResp = getAnswer('EnadeProvas/'+ano+'/'+area+'/Gabarito.pdf')
            saveDicResp('EnadeProvas/'+ano+'/'+area+'/', dicResp)

def getAnswer(PDF):

    with open(PDF, "rb") as f:
        pdf = pdftotext.PDF(f)

    gabarito = pdf[0] + ''
    line = gabarito.find('\n')
    gabarito = gabarito[line:]
    line = gabarito.find('1')
    gabarito = gabarito[line:]
    gabarito = gabarito.replace('\n', ' ')
    respostas = gabarito.split(' ')
    respostas = list(filter(lambda rm: rm != "", respostas))
    dicResp = {}
    i = 0
    while i < len(respostas)-1:
        dicResp[respostas[i]] = respostas[i+1]
        i += 2

    return dicResp

def saveDicResp(diretorio, dicResp):
    
    arqResp = open(diretorio+'Respostas.txt', 'w')
    for num in dicResp:
        arqResp.write(str(num)+'::'+str(dicResp[num])+'\n')
    arqResp.close()


if __name__ == '__main__':
    
    dicEnade = getDicEnade()
    extractQuestions(dicEnade)
    se.sendEmail('thiagoadriano2010@gmail.com', 'Extração de Questões Terminou', 'Todas as questões foram extraidas!!')
    extractAnswers(dicEnade)