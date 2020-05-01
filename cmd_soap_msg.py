# coding: latin-1
###############################################################################
# Teste das operações do serviço CMD (versão 1.6 da "CMD - Especificação dos serviços de
# Assinatura")
#
# Mensagens CMD SOAP
#
# cmd_soap_msg.py  (Python 3)
#
# Copyright (c) 2019 Devise Futures, Lda.
# Developed by José Miranda - jose.miranda@devisefutures.com
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
###############################################################################


"""
Funções que preparam e executam os comandos SOAP do SCMD, nomeadamente:
  + GetCertificate
          (applicationId: xsd:base64Binary, userId: xsd:string)
          -> GetCertificateResult: xsd:string
  + CCMovelSign
        (request: ns2:SignRequest)
        -> CCMovelSignResult: ns2:SignStatus
  + CCMovelMultipleSign
        (request: ns2:MultipleSignRequest, documents: ns2:ArrayOfHashStructure)
        -> CCMovelMultipleSignResult: ns2:SignStatus
  + ValidateOtp
        (code: xsd:string, processId: xsd:string,
            applicationId: xsd:base64Binary)
        -> ValidateOtpResult: ns2:SignResponse
"""

import hashlib            # hash SHA256
import logging.config     # debug
from zeep import Client   # zeep para SOAP
from zeep.transports import Transport


# Função para ativar o debug, permitindo mostrar mensagens enviadas e recebidas do servidor SOAP
def debug():
    """Activa o debug, mostrando as mensagens enviadas e recebidas do servidor SOAP."""
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'verbose': {'format': '>> %(name)s: %(message)s'}
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'zeep.transports': {
                'level': 'DEBUG',
                'propagate': True,
                'handlers': ['console'],
            },
        }
    })
    print('>> Debug: On')


# Função que devolve o URL do WSDL do SCMD (preprod ou prod)
def get_wsdl(env):
    """Devolve URL do WSDL do SCMD.

    Parameters
    ----------
    t : int
        WSDL a devolver: 0 para preprod, 1 para prod.

    Returns
    -------
    string
        URL do WSDL do SCMD.

    """
    wsdl = {
        0: 'https://preprod.cmd.autenticacao.gov.pt/Ama.Authentication.Frontend/CCMovelDigitalSignature.svc?wsdl',
        1: 'https://cmd.autenticacao.gov.pt/Ama.Authentication.Frontend/CCMovelDigitalSignature.svc?wsdl'
    }
    # Get the function from switcher dictionary
    return wsdl.get(env, lambda: 'No valid WSDL')


# Função que devolve o cliente de ligação (preprod ou prod) ao servidor SOAP da CMD
def getclient(env=0, timeout=10):
    """Devolve o cliente de ligação ao servidor SOAP da CMD.

    Parameters
    ----------
    env: int
        WSDL a devolver: 0 para preprod, 1 para prod.
    timeout: int
        Valor máximo que espera para estabelever ligação com o servidor SOAP da CMD

    Returns
    -------
    Zeep.Client
        Devolve o cliente de ligação ao servidor SOAP da CMD. Por defeito devolve o
        servidor de preprod.

    """
    transport = Transport(timeout=timeout)
    return Client(get_wsdl(env), transport=transport)


# Devolve a hash acrescentada do prefixo do tipo de hash utilizada
def hashPrefix(hashtype, hash):
    """Devolve a hash, à qual acrescenta o prefixo adequado ao hashtype utilizada.

    Parameters
    ----------
    hashtype : string ('SHA256')
        tipo de hash efetuada, do qual hash é o resultado.
    hash : byte
        hash digest

    Returns
    -------
    byte
        Devolve hash adicionada de prefixo adequado ao hashtype de hash utilizada.

    """
    prefix = {
        'SHA256': bytes(bytearray([0x30, 0x31, 0x30, 0x0d, 0x06, 0x09, 0x60, 0x86, 0x48, 0x01,
                                   0x65, 0x03, 0x04, 0x02, 0x01, 0x05, 0x00, 0x04, 0x20]))
    }
    return prefix.get(hashtype, lambda: 'Only SHA256 available') + hash


# GetCertificate(applicationId: xsd:base64Binary, userId: xsd:string)
#                                       -> GetCertificateResult: xsd:string
def getcertificate(client, args):
    """Prepara e executa o comando SCMD GetCertificate.

    Parameters
    ----------
    client : Client (zeep)
        Client inicializado com o WSDL.
    args : argparse.Namespace
        argumentos a serem utilizados na mensagem SOAP.

    Returns
    -------
    str
        Devolve o certificado do cidadão e a hierarquia de certificação.

    """
    request_data = {
        'applicationId': args.applicationId.encode('UTF-8'),
        'userId': args.user
    }
    return client.service.GetCertificate(**request_data)


# CCMovelSign(request: ns2:SignRequest) -> CCMovelSignResult: ns2:SignStatus
# ns2:SignRequest(ApplicationId: xsd:base64Binary, DocName: xsd:string,
#                  Hash: xsd:base64Binary, Pin: xsd:string, UserId: xsd:string)
# ns2:SignStatus(Code: xsd:string, Field: xsd:string, FieldValue: xsd:string,
#                   Message: xsd:string, ProcessId: xsd:string)
def ccmovelsign(client, args, hashtype='SHA256'):
    """Prepara e executa o comando SCMD CCMovelSign.

    Parameters
    ----------
    client : Client (zeep)
        Client inicializado com o WSDL.
    args : argparse.Namespace
        argumentos a serem utilizados na mensagem SOAP.
    hashtype: Tipo de hash
        tipo de hash efetuada, do qual o digest args.hash é o resultado.

    Returns
    -------
    SignStatus(Code: xsd:string, Field: xsd:string, FieldValue: xsd:string, Message: xsd:string,
    ProcessId: xsd:string)
        Devolve uma estrutura SignStatus com a resposta do CCMovelSign.

    """
    if 'docName' not in args:
        args.docName = 'docname teste'
    if 'hash' not in args:
        args.hash = hashlib.sha256(b'Nobody inspects the spammish repetition').digest()
    args.hash = hashPrefix(hashtype, args.hash)
    request_data = {
        'request': {
            'ApplicationId': args.applicationId.encode('UTF-8'),
            'DocName': args.docName,
            'Hash': args.hash,
            'Pin': args.pin,
            'UserId': args.user
        }
    }
    return client.service.CCMovelSign(**request_data)


# CCMovelMultipleSign(request: ns2:MultipleSignRequest,
#                              documents: ns2:ArrayOfHashStructure)
#                                  -> CCMovelMultipleSignResult: ns2:SignStatus
# ns2:MultipleSignRequest(ApplicationId: xsd:base64Binary, Pin: xsd:string,
#                                                           UserId: xsd:string)
# ns2:ArrayOfHashStructure(HashStructure: ns2:HashStructure[])
# ns2:HashStructure(Hash: xsd:base64Binary, Name: xsd:string, id: xsd:string)
# ns2:SignStatus(Code: xsd:string, Field: xsd:string, FieldValue: xsd:string,
#                   Message: xsd:string, ProcessId: xsd:string)
def ccmovelmultiplesign(client, args):
    """Prepara e executa o comando SCMD CCMovelMultipleSign.

    Parameters
    ----------
    client : Client (zeep)
        Client inicializado com o WSDL.
    args : argparse.Namespace
        argumentos a serem utilizados na mensagem SOAP.

    Returns
    -------
    SignStatus
        Devolve uma estrutura SignStatus com a resposta do CCMovelMultipleSign.

    """
    request_data = {
        'request': {
            'ApplicationId': args.applicationId.encode('UTF-8'),
            'Pin': args.pin,
            'UserId': args.user
        },
        'documents': {
            'HashStructure': [
                {'Hash': hashlib.sha256(b'Nobody inspects the spammish repetition').digest(),
                 'Name': 'docname teste1', 'id': '1234'},
                {'Hash': hashlib.sha256(b'Always inspect the spammish repetition').digest(),
                 'Name': 'docname teste2', 'id': '1235'}
                ]}
    }
    return client.service.CCMovelMultipleSign(**request_data)


# ValidateOtp(code: xsd:string, processId: xsd:string, applicationId:
#                      xsd:base64Binary) -> ValidateOtpResult: ns2:SignResponse
# ns2:SignResponse(ArrayOfHashStructure: ns2:ArrayOfHashStructure,
#                          Signature: xsd:base64Binary, Status: ns2:SignStatus)
# ns2:ArrayOfHashStructure(HashStructure: ns2:HashStructure[])
# ns2:HashStructure(Hash: xsd:base64Binary, Name: xsd:string, id: xsd:string)
# ns2:SignStatus(Code: xsd:string, Field: xsd:string, FieldValue: xsd:string,
#                                   Message: xsd:string, ProcessId: xsd:string)
def validate_otp(client, args):
    """Prepara e executa o comando SCMD ValidateOtp.

    Parameters
    ----------
    client : Client (zeep)
        Client inicializado com o WSDL.
    args : argparse.Namespace
        argumentos a serem utilizados na mensagem SOAP.

    Returns
    -------
    SignResponse
        Devolve uma estrutura SignResponse com a resposta do CCMovelMultipleSign.

    """
    request_data = {
        'applicationId': args.applicationId.encode('UTF-8'),
        'processId': args.ProcessId,
        'code': args.OTP,
    }
    return client.service.ValidateOtp(**request_data)
