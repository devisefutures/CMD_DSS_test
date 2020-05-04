# CMD-DSS  - Teste do serviço SCMD (Signature CMD) com o Digital Signature Service (DSS)

Nesta diretoria encontra uma aplicação com interface comando de linha (cli) que permite assinar um ficheiro PDF (assinatura "PAdES_BASELINE_B") recorrendo a:

+ [serviço de assinatura CMD](https://www.autenticacao.gov.pt/cmd-assinatura) (versão 1.6 da "CMD - Especificação dos serviços de Assinatura"),
+ [webapp DSS](https://ec.europa.eu/cefdigital/DSS/webapp-demo/home) (versão 5.6),
+ linguagem de programação [python](https://www.python.org/) (versão 3 (3.7.4)) 

Os ficheiros python têm a seguinte finalidade:

+ cmd_soap_msg.py - contém as funções que preparam e executam os 'comandos' SOAP do SCMD;
+ dss_rest_msg.py - contém as funções que preparam e executam os 'comandos' REST do DSS;
+ \_signpdf_config.py - Ficheiro que deve ser renomeado para signpdf_config.py e onde deve colocar o ApplicationId fornecido pela AMA, assim como o servidor DSS REST (no caso de utilizar servidor próprio).
+ signpdf_cli.py - Aplicação que permite assinar um ficheiro PDF.


### 1. Utilização da aplicação signpdf_cli

Os parâmetros e opções da _command line interface_ (CLI) da aplicação signpdf_cli podem
ser visualizadas  através da execução de `python3 signpdf_cli.py -h`.

Existem três parâmetros obrigatórios:

+ user - utilizador CMD (número de telemóvel),
+ pin - pin de assinatura CMD,
+ infile - ficheiro PDF a assinar,

e dois parâmetros opcionais:

+ "-outfile \<nome ficheiro\>" - nome do ficheiro onde gravar o ficheiro assinado. Se este parâmetro não for fornecido, o nome do ficheiro será o nome de _infile_ acrescido de ".signed",
+ "-datetime \<dia e hora\>" - dia e hora da assinatura no formato 'DD/MM/AAAA  hh:mm:ss'. Se este parâmetro não for fornecido, será utilizada o dia e hora atual.

#### 1.1 Exemplo de Utilização

A assinatura do ficheiro teste.pdf com a data e hora actual e a ser gravado para teste.signed.pdf é efetuada do seguinte modo:

> `python3 signpdf_cli.py '+351 000000000' 12345678 teste.pdf`

A assinatura do ficheiro teste.pdf no dia 12 de Fevereiro de 2020 às 12:45:56 e a ser gravado para old.pdf é efetuada do seguinte modo:

> `python3 signpdf_cli.py '+351 000000000' 12345678 teste.pdf -datetime '12/02/2020 12:45:56' -outfile old.pdf`

### 2. Notas genéricas

1. Necessário instalar o python3 na sua máquina (ver em <https://www.python.org/downloads/)>

2. Necessário instalar as seguintes packages python, por exemplo com recurso ao
pip3 (caso ainda não estejam instalados):

    - sys
    - argparse  
    - hashlib  
    - datetime
    - pem
    - requests
    - base64
    - json
    - re
    - os
    - logging 
    - zeep

    Note que é provável que todos estejam instalados por omissão, à excepção das packages pem e zeep.

3. A aplicação foi testada com Python 3.7.4 e Python 3.6.9

4. Antes de utilizar, renomeie o ficheiro \_signpdf_config.py para signpdf_config.py
e introduza o APPLICATION_ID da sua entidade (atribuído pela AMA), assim como altere o servidor DSS REST no caso de estar a utilizar um servidor diferente daquele que está indicado.

5. A aplicação está a contactar com um servidor WebApp DSS, instalado em <https://dss.devisefutures.com/>, sendo enviado o ficheiro PDF para esse servidor. Por uma questão de confidencialidade dos seus dados, deverá instalar o servidor WebApp DSS no seu próprio servidor (pode obter o DSS _bundle_ em <https://ec.europa.eu/cefdigital/wiki/display/CEFDIGITAL/DSS)> e alterar o URL do DSS_REST no ficheiro signpdf_config.py.

6. A comunicação com o servidor CMD é direta, sem intermediação do servidor WebApp DSS. Ou seja, o _user_ e o _pin_ são comunicados diretamente do seu computador com o servidor CMD.

7. Licença: GNU GENERAL PUBLIC LICENSE Version 3
