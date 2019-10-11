
import smtplib

from string import Template

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# import sys
# import argparse

MY_ADDRESS = 'thiagoadriano2010@gmail.com'
PASSWORD = ''

def sendEmail(e, t, m):
   
    # parser = argparse.ArgumentParser(description='Argumentos para enviar o email.')
    # parser.add_argument('-e', required=True, help= "email de destino")
    # parser.add_argument('-t', required=False, help= "titulo do email")
    # parser.add_argument('-m', required=False, help= "mensagem do email")

    # args = parser.parse_args()

    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.login(MY_ADDRESS, PASSWORD)

    msg = MIMEMultipart()       # create a message
    # message = args.m
    message = m

    msg['From'] = MY_ADDRESS
    # msg['To']= args.e
    msg['To']= e
    # msg['Subject']= args.t
    msg['Subject']= t
    
    msg.attach(MIMEText(message, 'plain'))
    
    s.send_message(msg)
    del msg
    s.quit()
    print("Email enviado com sucesso!")
    
# if __name__ == '__main__':
    # main()
    # print("Email enviado com sucesso!")