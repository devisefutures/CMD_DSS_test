# coding: latin-1
###############################################################################
# Teste das operações do serviço DSS (versão 5.6 do DSS)
#
# Mensagens DSS REST
#
# dss_rest_msg.py  (Python 3)
#
# Copyright (c) 2020 Devise Futures, Lda.
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
Funções que preparam e executam os comandos REST do DSS, nomeadamente:
  + getDataToSign(dataToSignDTO: ns0:dataToSignOneDocumentDTO) 
            -> response: ns0:toBeSignedDTO
  + signDocument(signDocumentDTO: ns0:signOneDocumentDTO) 
            -> response: ns0:remoteDocument
"""

import hashlib            # hash SHA256
import requests
import base64


# getDataToSign(dataToSignDTO: ns0:dataToSignOneDocumentDTO) -> response: ns0:toBeSignedDTO
# ns0:dataToSignOneDocumentDTO(parameters: ns0:remoteSignatureParameters,
#                                                           toSignDocument: ns0:remoteDocument)
# ns0:remoteSignatureParameters(archiveTimestampParameters: ns0:remoteTimestampParameters,
#       asicContainerType: ns0:aSiCContainerType,
#       BLevelParams: ns0:remoteBLevelParameters,
#       certificateChain: ns0:remoteCertificate[],
#       contentTimestampParameters: ns0:remoteTimestampParameters,
#       contentTimestamps: ns0:timestampDTO[],
#       detachedContents: ns0:remoteDocument[],
#       digestAlgorithm: ns0:digestAlgorithm,
#       encryptionAlgorithm: ns0:encryptionAlgorithm,
#       generateTBSWithoutCertificate: xsd:boolean,
#       maskGenerationFunction: ns0:maskGenerationFunction,
#       referenceDigestAlgorithm: ns0:digestAlgorithm,
#       signWithExpiredCertificate: xsd:boolean,
#       signatureLevel: ns0:signatureLevel,
#       signaturePackaging: ns0:signaturePackaging,
#       signatureTimestampParameters: ns0:remoteTimestampParameters,
#       signingCertificate: ns0:remoteCertificate)
# ns0:remoteTimestampParameters(canonicalizationMethod: xsd:string, digestAlgorithm: ns0:digestAlgorithm,
#       timestampContainerForm: ns0:timestampContainerForm)
# ns0:remoteBLevelParameters(claimedSignerRoles: xsd:string[], commitmentTypeIndications: xsd:string[],
#       policyDescription: xsd:string, policyDigestAlgorithm: ns0:digestAlgorithm,
#       policyDigestValue: xsd:base64Binary, policyId: xsd:string, policyQualifier: xsd:string,
#       policySpuri: xsd:string, signerLocationCountry: xsd:string, signerLocationLocality: xsd:string,
#       signerLocationPostalAddress: xsd:string[], signerLocationPostalCode: xsd:string,
#       signerLocationStateOrProvince: xsd:string, signerLocationStreet: xsd:string,
#       signingDate: xsd:dateTime, trustAnchorBPPolicy: xsd:boolean)
# ns0:remoteCertificate(encodedCertificate: xsd:base64Binary)
# ns0:timestampDTO(binaries: xsd:base64Binary, canonicalizationMethod: xsd:string,
#       includes: ns0:timestampIncludeDTO[], type: ns0:timestampType)
# ns0:timestampIncludeDTO(referencedData: xsd:boolean, URI: xsd:string)
# ns0:remoteDocument(bytes: xsd:base64Binary, digestAlgorithm: ns0:digestAlgorithm, name: xsd:string)
# ns0:toBeSignedDTO(bytes: xsd:base64Binary)
def getDataToSign(certs_chain, signdate, pdf, dss_rest):
    """Prepara e executa o comando DSS getDataToSign.

    Parameters
    ----------
    certs_chain : array de certificados
        Contém certificado de assinatura, EC intermédia e Root.
    signdate : datetime, em formato ISO 
        Data e hora de assinatura em formato ISO.
    pdf: Estrutura com ficheiro e nome do ficheiro
        PDF a assinar e nome do ficheiro de onde foi lido.
    dss_rest: URI
        Servidor DSS Rest - Web Services

    Returns
    -------
    ns0:toBeSignedDTO(bytes: xsd:base64Binary)
        Devolve o DTBS (i.e., Data to be signed) do PDF.
    """
    request_data = {
        "parameters": {
            "signWithExpiredCertificate": False,
            "generateTBSWithoutCertificate": False,
            "signatureLevel": "PAdES_BASELINE_B",
            "signaturePackaging": "ENVELOPED",
            "encryptionAlgorithm": "RSA",
            "digestAlgorithm": "SHA256",
            "referenceDigestAlgorithm": None,
            "maskGenerationFunction": None,
            "signingCertificate": {
                "encodedCertificate": certs_chain['sign']
            },
            "certificateChain": [
                {"encodedCertificate": certs_chain['root']},
                {"encodedCertificate": certs_chain['ca']}
            ],
            "detachedContents": None,
            "asicContainerType": None,
            "blevelParams": {
                "trustAnchorBPPolicy": True,
                "signingDate": signdate,
                "claimedSignerRoles": None,
                "commitmentTypeIndications": None
            }
        },
        "toSignDocument": {
            "bytes": base64.b64encode(pdf['bytes']).decode(),
            "name": pdf['name'],
        }
    }
    return requests.post(dss_rest + '/getDataToSign', json=request_data)


# signDocument(signDocumentDTO: ns0:signOneDocumentDTO) -> response: ns0:remoteDocument
# ns0:signOneDocumentDTO(parameters: ns0:remoteSignatureParameters, signatureValue: ns0:signatureValueDTO,
#                                                           toSignDocument: ns0:remoteDocument)
# ns0:signatureValueDTO(algorithm: ns0:signatureAlgorithm, value: xsd:base64Binary)
# ns0:remoteSignatureParameters(archiveTimestampParameters: ns0:remoteTimestampParameters,
#       asicContainerType: ns0:aSiCContainerType,
#       BLevelParams: ns0:remoteBLevelParameters,
#       certificateChain: ns0:remoteCertificate[],
#       contentTimestampParameters: ns0:remoteTimestampParameters,
#       contentTimestamps: ns0:timestampDTO[],
#       detachedContents: ns0:remoteDocument[],
#       digestAlgorithm: ns0:digestAlgorithm,
#       encryptionAlgorithm: ns0:encryptionAlgorithm,
#       generateTBSWithoutCertificate: xsd:boolean,
#       maskGenerationFunction: ns0:maskGenerationFunction,
#       referenceDigestAlgorithm: ns0:digestAlgorithm,
#       signWithExpiredCertificate: xsd:boolean,
#       signatureLevel: ns0:signatureLevel,
#       signaturePackaging: ns0:signaturePackaging,
#       signatureTimestampParameters: ns0:remoteTimestampParameters,
#       signingCertificate: ns0:remoteCertificate)
# ns0:remoteTimestampParameters(canonicalizationMethod: xsd:string, digestAlgorithm: ns0:digestAlgorithm,
#       timestampContainerForm: ns0:timestampContainerForm)
# ns0:remoteBLevelParameters(claimedSignerRoles: xsd:string[], commitmentTypeIndications: xsd:string[],
#       policyDescription: xsd:string, policyDigestAlgorithm: ns0:digestAlgorithm,
#       policyDigestValue: xsd:base64Binary, policyId: xsd:string, policyQualifier: xsd:string,
#       policySpuri: xsd:string, signerLocationCountry: xsd:string, signerLocationLocality: xsd:string,
#       signerLocationPostalAddress: xsd:string[], signerLocationPostalCode: xsd:string,
#       signerLocationStateOrProvince: xsd:string, signerLocationStreet: xsd:string,
#       signingDate: xsd:dateTime, trustAnchorBPPolicy: xsd:boolean)
# ns0:remoteCertificate(encodedCertificate: xsd:base64Binary)
# ns0:timestampDTO(binaries: xsd:base64Binary, canonicalizationMethod: xsd:string,
#       includes: ns0:timestampIncludeDTO[], type: ns0:timestampType)
# ns0:remoteDocument(bytes: xsd:base64Binary, digestAlgorithm: ns0:digestAlgorithm, name: xsd:string)
def signDocument(certs_chain, signdate, pdf, res, dss_rest):
    """Prepara e executa o comando DSS getDataToSign.

    Parameters
    ----------
    certs_chain : array de certificados
        Contém certificado de assinatura, EC intermédia e Root.
    signdate : datetime, em formato ISO 
        Data e hora de assinatura em formato ISO.
    pdf: Estrutura com ficheiro e nome do ficheiro
        PDF a assinar e nome do ficheiro de onde foi lido.
    res: Estrutura com assinatura
        Assinatura do PDF
    dss_rest: URI
        Servidor DSS Rest - Web Services

    Returns
    -------
    ns0:remoteDocument(bytes: xsd:base64Binary, digestAlgorithm: ns0:digestAlgorithm, name: xsd:string)
        Devolve uma estrutura com o PDF assinado (bytes).
    """
    request_data = {
        "parameters": {
            "signWithExpiredCertificate": False,
            "generateTBSWithoutCertificate": False,
            "signatureLevel": "PAdES_BASELINE_B",
            "signaturePackaging": "ENVELOPED",
            "encryptionAlgorithm": "RSA",
            "digestAlgorithm": "SHA256",
            "referenceDigestAlgorithm": None,
            "maskGenerationFunction": None,
            "signingCertificate": {
                "encodedCertificate": certs_chain['sign']
            },
            "certificateChain": [
                {"encodedCertificate": certs_chain['root']},
                {"encodedCertificate": certs_chain['ca']}
            ],
            "detachedContents": None,
            "asicContainerType": None,
            "blevelParams": {
                "trustAnchorBPPolicy": True,
                "signingDate": signdate,
                "claimedSignerRoles": None,
                "commitmentTypeIndications": None
            }
        },
        "signatureValue": {
            "algorithm": "RSA_SHA256",
            "value": base64.b64encode(res['Signature']).decode()
        },
        "toSignDocument": {
            "bytes": base64.b64encode(pdf['bytes']).decode(),
            "name": pdf['name'],
        }
    }
    return requests.post(dss_rest + '/signDocument', json=request_data)
