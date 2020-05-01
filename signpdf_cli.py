# coding: latin-1
###############################################################################
# Comando linha de assinatura PAdES de ficheiros PDF, através da CMD e DSS
# Aplicação de teste para aquilatar a utilização do CMD com o DSS
#
# signpdf_cli.py  (Python 3)
#
# Copyright (c) 2019-2020 Devise Futures, Lda.
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
Linha de comando para assinar um documento PDF através do DSS e CMD.
"""

import sys
import argparse           # parsing de argumentos comando linha
import hashlib            # hash SHA256
from datetime import datetime
import pem
import base64
import json
import re
import os
import logging              # debug


import signpdf_config
import dss_rest_msg
import cmd_soap_msg


TEXT = 'PDF PAdES (DSS & CMD) signature Command Line Program, by DeviseFutures, Lda.'
VERSION = 'version: 1.0'


def main():
    """Função main do programa."""
    args = args_parse()
    if len(sys.argv) > 1:
        if args.debug:
            logging.basicConfig(level=logging.DEBUG)
        client = cmd_soap_msg.getclient(1)
        args.applicationId = signpdf_config.get_appid()
        args.dss_rest = signpdf_config.get_rest()
        if args.outfile is None:
            (h, t) = os.path.splitext(args.infile)
            args.outfile = h + ".signed" + t
        signpdf(client, args)
    else:
        print('Use -h for usage:\n  ', sys.argv[0], '-h')


def args_parse():
    """Define as várias opções do comando linha."""
    parser = argparse.ArgumentParser(description=TEXT)
    parser.add_argument('-V', '--version', help='show program version', action='version',
                        version=VERSION)
    parser.add_argument('user', action='store',
                        help='user phone number (+XXX NNNNNNNNN)')
    parser.add_argument('pin', action='store', help='CMD signature PIN')
    parser.add_argument('infile', action='store', help='PDF file to sign')
    parser.add_argument('-outfile', action='store',
                        help='Signed PDF file (default: <infile>.signed.pdf)')
    parser.add_argument('-datetime', action='store',
                        help='"DD/MM/YYYY hh:mm:ss" format (default: current time and date)')
    parser.add_argument(
        '-D', '--debug', help='show debug information', action='store_true')
    return parser.parse_args()


def signpdf(client, args):
    """Assina o PDF em formato PAdES, recorrendo ao DSS e CMD.

    Parameters
    ----------
    args : dictionary
        Parâmetros passado pelo comando linha.

    Returns
    -------
    int
        Devolve 0 na conclusão com sucesso da função.

    """
    # Obtém cadeia de certificados CMD
    cmd_certs = cmd_soap_msg.getcertificate(client, args)
    if cmd_certs is None:
        print('Impossível obter certificado CMD')
        exit()

    # certs[0] = user; certs[1] = root; certs[2] = CA
    certs = pem.parse(cmd_certs.encode())

    certs_chain = {'sign': re.sub('\s*-----\s*(BEGIN|END) CERTIFICATE\s*-----\s*', '', certs[0].as_text()). replace('\n', ''),
                   'ca': re.sub('\s*-----\s*(BEGIN|END) CERTIFICATE\s*-----\s*', '', certs[2].as_text()).replace('\n', ''),
                   'root': re.sub('\s*-----\s*(BEGIN|END) CERTIFICATE\s*-----\s*', '', certs[1].as_text()).replace('\n', '')
                   }

    # Lê ficheiro PDF
    try:
        with open(args.infile, "rb") as file:
            pdf_file = file.read()
    except Exception as e:
        print("Ficheiro " + args.infile + " não encontrado.")
        exit()
    pdf = {'bytes': pdf_file, 'name': args.infile}

    # Identifica hora/data de assinatura
    if args.datetime:
        signdate = datetime.strptime(
            args.datetime, '%d/%m/%Y %H:%M:%S').isoformat()
    else:
        signdate = datetime.now().isoformat()

    # Obtém o DTBS do PDF e gera a hash a assinar
    response = dss_rest_msg.getDataToSign(
        certs_chain, signdate, pdf, args.dss_rest)
    dtbs = response.json()['bytes']
    args.hash = hashlib.sha256(base64.b64decode(dtbs)).digest()
    args.docName = args.infile

    # Obtém assinatura da hash
    res = cmd_soap_msg.ccmovelsign(client, args)
    if res['Code'] != '200':
        print('Erro ' + res['Code'] + '. Valide o PIN introduzido.')
        exit()
    vars(args)['ProcessId'] = res['ProcessId']
    vars(args)['OTP'] = input('Introduza o OTP recebido no seu dispositivo: ')
    res = cmd_soap_msg.validate_otp(client, args)
    if res['Status']['Code'] != '200':
        print('Erro ' + res['Status']['Code'] +
              '. ' + res['Status']['Message'])
        exit()

    # Assina PDF
    response = dss_rest_msg.signDocument(
        certs_chain, signdate, pdf, res, args.dss_rest)

    # Grava PDF
    with open(args.outfile, 'wb') as file:
        file.write(base64.b64decode(response.json()['bytes']))
    print("Ficheiro assinado guardado em " + args.outfile)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except:  # catch *all* exceptions
        e = sys.exc_info()
        print("Erro: %s" % str(e))
        exit()
