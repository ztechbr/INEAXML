# INEA XML - Monitoramento de Alertas de Cheias

Aplicação Flask para exibir dados de estações hidrológicas do INEA (Instituto Estadual do Ambiente do Rio de Janeiro) em uma tabela organizada com Tailwind CSS.

## Características

-  Atualização automática dos dados a cada 5 minutos
-  Tabela responsiva com Tailwind CSS
-  Filtro por município/cidade
-  Interface moderna e intuitiva
-  Exibição de dados de chuva e nível dos rios

## Instalação

1. Clone ou baixe este repositório

2. Crie um ambiente virtual (recomendado):
```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

Execute a aplicação:
```bash
python app.py
```

Acesse no navegador:
```
http://localhost:4001
```

## Estrutura do Projeto

```
INEAXML/
├── app.py              # Aplicação Flask principal
├── requirements.txt    # Dependências Python
├── Dockerfile          # Configuração Docker
├── docker-compose.yml  # Compose para orquestração
├── .dockerignore       # Arquivos ignorados no build
├── README.md          # Este arquivo
└── templates/
    └── index.html     # Template HTML com Tailwind CSS
```

## Deploy com Docker

### Usando Docker Compose

1. Construa e inicie o container:
```bash
docker-compose up -d --build
```

2. Acesse a aplicação:
```
http://localhost:4001
```

3. Para parar:
```bash
docker-compose down
```

### Usando Docker diretamente

1. Construa a imagem:
```bash
docker build -t inea-xml .
```

2. Execute o container:
```bash
docker run -d -p 4001:4001 --name inea-xml-app inea-xml
```

## Deploy no Easypanel

1. Conecte seu repositório Git ao Easypanel
2. Selecione o tipo de aplicação: **Docker**
3. Configure:
   - **Porta**: `4001`
   - **Build Command**: (deixe vazio, usa o Dockerfile)
   - **Start Command**: (deixe vazio, usa o CMD do Dockerfile)
4. O Easypanel detectará automaticamente o `Dockerfile` e `docker-compose.yml`
5. Faça o deploy!

## Funcionalidades

### Atualização Automática
Os dados são buscados automaticamente do XML do INEA a cada 5 minutos em uma thread separada.

### Filtro por Município
Use o dropdown no topo da página para filtrar as estações por município. Você também pode limpar o filtro para ver todas as estações.

### Dados Exibidos
- ID da estação
- Nome da estação
- Município
- Nome do rio
- Horário da última leitura
- Dados de chuva (última, 1h, 4h, 24h, 96h)
- Níveis do rio (último, 15min, 30min, 45min)
- Coordenadas (latitude e longitude)

## API

A aplicação também fornece uma API JSON em:
```
http://localhost:4001/api/data
```

Parâmetros opcionais:
- `cidade`: Filtrar por município

Exemplo:
```
http://localhost:4001/api/data?cidade=Itaperuna
```

## Tecnologias Utilizadas

- **Flask**: Framework web Python
- **Tailwind CSS**: Framework CSS utilitário
- **Requests**: Biblioteca para requisições HTTP
- **xml.etree.ElementTree**: Parser XML nativo do Python

## Fonte dos Dados

Os dados são obtidos de:
https://alertadecheias.inea.rj.gov.br/alertadecheias/dados.xml

## Notas

- A página é atualizada automaticamente a cada 5 minutos via meta refresh
- Os dados são atualizados em background sem interromper a navegação
- A aplicação busca os dados imediatamente ao iniciar

