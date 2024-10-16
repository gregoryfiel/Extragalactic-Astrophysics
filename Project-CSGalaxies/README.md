# Project CSGalaxies

### Análise de dados do MaNGA com API Marvin

O **Project CSGalaxies** é um projeto voltado para a análise de dados do programa **Mapping Nearby Galaxies at Apache Point Observatory (MaNGA)**, utilizando a API Marvin para acessar e manipular os dados. O objetivo é criar scripts e ferramentas que facilitem a análise e visualização dos dados astronômicos, com foco no estudo de galáxias extragalácticas.

## Estrutura do Projeto

O projeto é organizado da seguinte maneira:

```bash
ProjectCSGalaxies/
│
├── landing/
├── curated/
├── src/ 
│   ├── main.py
│   └── ...
├── tests/
│   └── test_src.py
├── README.md 
├── requirements.txt 
├── setup.py 
└── venv/
```

### Principais Pastas
* landing/: Contém os dados brutos baixados diretamente da API.
curated/: Contém os dados já processados e prontos para análise.
* src/: Onde o código-fonte do projeto está localizado. Todo o código principal é implementado aqui, organizado em módulos e classes.
* tests/: Contém testes automatizados usando unittest ou outras ferramentas de teste, garantindo a integridade do código durante o desenvolvimento.

## Instalação
### Pré-requisitos
Certifique-se de ter o Python 3.7 ou superior instalado. Recomenda-se o uso de um ambiente virtual para isolar as dependências do projeto.

### Passos para Instalação
1. Clone o repositório:
```bash
git clone https://github.com/gregoryfiel/Extragalactic-Astrophysics.git
cd Extragalactic-Astrophysics
```
2. Crie um ambiente virtual (opcional, mas recomendado):
```bash
python -m venv venv
source venv/bin/activate   # No Windows, use venv\Scripts\activate
```
3. Instale as dependências: As dependências principais do projeto estão listadas no `setup.py` e `requirements.txt`.
Para instalar as dependências principais:
```bash
pip install .
```
Para instalar as dependências de desenvolvimento (testes, linters, etc.):
```bash
pip install .[dev]
```
4. Configuração do Projeto: Após a instalação, você poderá começar a trabalhar no projeto, usando a estrutura de módulos em `src/` para adicionar novas funcionalidades ou scripts de análise.

## Uso
O objetivo principal do projeto é facilitar a análise dos dados do MaNGA. Exemplos de uso serão adicionados à medida que o desenvolvimento avançar. Você poderá usar scripts dentro de src/ para consumir a API Marvin e manipular os dados das galáxias.

### Exemplo Básico
Aqui está um exemplo de como você pode começar a usar a API Marvin para acessar os dados:
```bash
pass
```
## Testes
Para garantir que os módulos do projeto estão funcionando corretamente, você pode rodar os testes automatizados localizados na pasta `tests/`.

Para rodar todos os testes com `unittest`, use o comando:
```bash
python -m unittest discover -s tests
```

## Autores
Gregory Peruzzo Fiel <br>
Marina Trevisan, PhD - Orientadora

## Licença
Este projeto está licenciado sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.