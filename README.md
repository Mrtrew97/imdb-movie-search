# Motor de Pesquisa de Filmes IMDb

> **Projeto Final – Programação em Python**  
> **Master.D**  
> **Autor:** Bruno Pinto  
> **Ano:** 2026  
> **Classificação Final:** 🏆 *Em Breve*

---

## ✨ Características Principais

* ✔ **Motor de pesquisa de filmes** baseado no dataset dos 1000 melhores filmes do IMDb.
* ✔ **Pesquisa aproximada (*fuzzy matching*)** com tolerância a erros de escrita e variações nos termos pesquisados.
* ✔ **Pesquisa por equivalências em Português de Portugal**, relacionando títulos e expressões em português com os respetivos títulos originais em inglês.
* ✔ **Tratamento e limpeza de dados** utilizando `pandas` antes da apresentação e pesquisa dos filmes.
* ✔ **Interface web interativa** desenvolvida com Streamlit.
* ✔ **Suporte multilíngue (PT / EN)** através de ficheiros externos de tradução.
* ✔ **Vista em grelha e vista em tabela** para apresentação dos resultados.
* ✔ **Ordenação dinâmica** por relevância, classificação, ano, duração e título.
* ✔ **Paginação configurável** com diferentes quantidades de resultados por página.
* ✔ **Persistência do estado da aplicação através de parâmetros no URL**.
* ✔ **Cache de dados e traduções** para reduzir processamento desnecessário.
* ✔ **Proteção do conteúdo apresentado** através do tratamento seguro de dados provenientes do dataset.

---

## 🚀 Tecnologias, Bibliotecas e Linguagens Utilizadas

* **Python** — linguagem principal utilizada no desenvolvimento da aplicação, processamento dos dados e implementação do motor de pesquisa.
* **Pandas** — importação, manipulação, limpeza e tratamento do conjunto de dados dos filmes.
* **RapidFuzz** — implementação da correspondência aproximada (fuzzy matching) e cálculo de similaridade entre os termos pesquisados e os títulos dos filmes.
* **Streamlit** — desenvolvimento da interface web interativa e gestão da interação com o utilizador.
* **CSS3** — personalização da apresentação visual e identidade gráfica da aplicação.
* **JSON** — armazenamento dos textos de tradução da interface e do sistema de equivalências linguísticas entre títulos em Português de Portugal e títulos originais em inglês.

---

## 📁 Estrutura Principal

```text
.
├── app.py
├── requirements.txt
├── top_1000_imdb_movies.csv
├── style.css
├── README.md
├── locales/
│   ├── pt.json
│   ├── en.json
│   └── equivalencias_pt.json
└── .streamlit/
    └── config.toml
```

- `app.py` — contém a lógica principal da aplicação, incluindo o carregamento e tratamento dos dados, o motor de pesquisa e a interface desenvolvida com Streamlit.
- `requirements.txt` — lista as bibliotecas Python necessárias para instalar e executar a aplicação.
- `top_1000_imdb_movies.csv` — conjunto de dados utilizado pela aplicação, contendo os filmes do ranking dos 1000 melhores filmes do IMDb.
- `style.css` — contém os estilos CSS utilizados para personalizar a apresentação visual da aplicação.
- `locales/pt.json` — contém os textos da interface em Português.
- `locales/en.json` — contém os textos da interface em Inglês.
- `locales/equivalencias_pt.json` — contém as equivalências de títulos e expressões em Português de Portugal utilizadas pelo motor de pesquisa.
- `.streamlit/config.toml` — contém as configurações do Streamlit e os parâmetros do tema visual da aplicação.
- `README.md` — documentação do projeto, incluindo a sua estrutura, funcionalidades, tecnologias e instruções de execução.

---

## 🔎 Motor de Pesquisa

O motor de pesquisa foi desenvolvido para permitir encontrar filmes através de correspondência exata e aproximada, mesmo quando o termo pesquisado contém erros de escrita, diferenças de composição ou utiliza uma designação em Português de Portugal.

A pesquisa combina diferentes estratégias de correspondência para calcular a relevância dos resultados:

### 1. Correspondência direta

É verificado se o termo pesquisado corresponde diretamente ou está presente no título de um filme. Esta abordagem permite identificar rapidamente correspondências claras entre a pesquisa e os títulos existentes no dataset.

### 2. Correspondência por palavras

O termo pesquisado é dividido em palavras individuais e cada palavra é comparada com os diferentes elementos dos títulos disponíveis. A similaridade obtida nas correspondências é utilizada para calcular uma pontuação média para o filme.

Esta abordagem permite lidar melhor com pesquisas compostas por várias palavras e com pequenas diferenças na sua ordem ou escrita.

### 3. Correspondência aproximada com RapidFuzz

A biblioteca rapidfuzz é utilizada através do algoritmo WRatio para calcular a similaridade entre o termo pesquisado e os títulos dos filmes.

Este mecanismo permite encontrar resultados mesmo quando existem:

- erros ortográficos;
- gralhas;
- diferenças de capitalização;
- pequenas variações na escrita;
- diferenças na composição do título.

### 4. Equivalências linguísticas

O motor utiliza o ficheiro locales/equivalencias_pt.json para reconhecer títulos e expressões em Português de Portugal e relacioná-los com os respetivos títulos originais em inglês.

Desta forma, uma pesquisa utilizando uma designação conhecida em português pode ser associada ao título correspondente existente no dataset.

### 5. Combinação das pontuações

Quando são encontradas equivalências linguísticas, a pontuação obtida através da equivalência é combinada com a pontuação correspondente ao título original.

A aplicação utiliza estas pontuações para determinar a relevância final de cada resultado.

### 6. Deduplicação e ordenação

Depois de aplicadas as diferentes estratégias de pesquisa, os resultados são deduplicados para evitar que o mesmo filme seja apresentado várias vezes.

Cada filme é posteriormente associado à melhor pontuação de similaridade obtida e os resultados são ordenados de acordo com a sua relevância.

Este processo permite apresentar primeiro os filmes que apresentam maior correspondência com o termo pesquisado, mantendo simultaneamente a capacidade de encontrar resultados perante pesquisas menos exatas.

---

## 🌐 Internacionalização

A aplicação foi desenvolvida com suporte para Português e Inglês (PT / EN), permitindo alterar o idioma da interface sem modificar a lógica principal da aplicação.

Os textos apresentados ao utilizador encontram-se separados da lógica da aplicação através de ficheiros JSON, facilitando a manutenção e a alteração das traduções.

### 🇵🇹 Português e 🇬🇧 Inglês

A interface disponibiliza dois idiomas:

* **Português (PT)** — idioma principal da aplicação.
* **Inglês (EN)** — versão alternativa da interface.

Os textos de cada idioma encontram-se armazenados nos ficheiros:

* **locales/pt.json**
* **locales/en.json**

A aplicação carrega os textos correspondentes ao idioma selecionado e utiliza-os nos diferentes elementos da interface.

### 🔤 Equivalências de títulos em Português de Portugal

Para além da tradução da interface, foi desenvolvido um sistema específico de equivalências linguísticas para permitir pesquisas utilizando títulos e expressões em Português de Portugal.

O ficheiro locales/equivalencias_pt.json contém associações entre designações em português e os respetivos títulos originais em inglês presentes no dataset.

Por exemplo, quando o utilizador pesquisa utilizando uma designação conhecida em português, o motor de pesquisa pode identificar a equivalência correspondente e utilizá-la na pesquisa do título original.

Esta funcionalidade permite que a pesquisa seja mais natural para utilizadores portugueses, sem necessidade de conhecer ou introduzir o título original em inglês.

### 🔄 Integração com o motor de pesquisa

As equivalências linguísticas não funcionam apenas como uma substituição direta do texto pesquisado. As correspondências encontradas no ficheiro de equivalências são integradas no sistema de relevância do motor de pesquisa.

As pontuações obtidas através das equivalências são combinadas com as pontuações calculadas através da correspondência aproximada dos títulos, contribuindo para a determinação da relevância final dos resultados.

Desta forma, a internacionalização da aplicação abrange tanto a interface de utilização como a forma de pesquisar os filmes, mantendo a experiência de pesquisa consistente nos dois idiomas.

---

## ▶️ Instalação e Execução

### 1. Clonar o Repositório

Clone o repositório para a máquina local e aceda à pasta do projeto:
```bash
git clone https://github.com/Mrtrew97/imdb-movie-search.git
cd imdb-movie-search
```

### 2. Instalar as Dependências

Com o Python instalado, execute o seguinte comando na pasta raiz do projeto:
```bash
pip install -r requirements.txt
```

O ficheiro `requirements.txt` contém as bibliotecas necessárias para executar a aplicação.

### 3. Iniciar a Aplicação

Execute a aplicação através do Streamlit:
```bash
python -m streamlit run app.py
```

### 4. Aceder à Aplicação

Após iniciar o servidor local, o Streamlit disponibiliza a aplicação através do endereço:
```text
http://localhost:8501
```

A aplicação pode então ser utilizada diretamente através do navegador.

---

## 📋 Principais Funcionalidades

### 🔎 Pesquisa de Filmes

- Pesquisa por título através de correspondência direta e aproximada.
- Tolerância a erros de escrita, gralhas e pequenas variações nos termos pesquisados.
- Pesquisa através de diferentes estratégias de correspondência para melhorar a relevância dos resultados.
- Utilização de equivalências de títulos e expressões em Português de Portugal.
- Apresentação da percentagem de similaridade associada aos resultados da pesquisa.

### 🎬 Catálogo de Filmes

- Apresentação dos filmes disponíveis no dataset dos 1000 melhores filmes do IMDb.
- Apresentação das principais informações de cada filme, incluindo título, classificação, ano de lançamento, duração e descrição.
- Ordenação dos resultados por relevância, classificação, ano, duração ou título.
- Possibilidade de ordenar os resultados de forma ascendente ou descendente.

### 🖥️ Modos de Visualização

- **Vista em grelha (*Grid View*)** para apresentação dos filmes através de cartões.
- **Vista em tabela (*Table View*)** para apresentação dos resultados de forma estruturada.
- Ordenação interativa das colunas na vista em tabela.
- Indicação visual da coluna atualmente utilizada para ordenação.

### 📄 Paginação e Navegação

- Seleção do número de filmes apresentados por página.
- Opções de 20, 50 ou 100 resultados por página.
- Navegação para a primeira, página anterior, página seguinte ou última página.
- Botão de regresso ao topo da página.

### 🌐 Idioma e Preferências

- Alternância entre Português e Inglês.
- Preservação do idioma selecionado durante a navegação.
- Persistência do termo de pesquisa, página, modo de visualização e critérios de ordenação através dos parâmetros do URL.

### ⚡ Desempenho e Gestão de Dados

- Carregamento e processamento do dataset através de `pandas`.
- Limpeza e normalização dos dados antes da utilização pela aplicação.
- Utilização de `st.cache_data` para evitar processamento desnecessário durante as reexecuções.
- Carregamento das traduções e equivalências linguísticas através de ficheiros JSON.
- Tratamento de ficheiros e valores ausentes de forma a evitar erros técnicos durante a utilização.

---

## 🛡️ Segurança

Embora o projeto seja uma aplicação de caráter académico e não envolva autenticação de utilizadores ou armazenamento de dados pessoais, foram aplicadas algumas medidas para garantir um tratamento seguro dos dados utilizados pela aplicação.

### 🔐 Proteção do Conteúdo Apresentado

Os títulos e descrições dos filmes são provenientes diretamente do dataset e podem conter caracteres ou conteúdo HTML.

Para evitar que este conteúdo seja interpretado como código HTML pela interface, é utilizada a função `html.escape()` antes da apresentação dos valores.

Esta medida impede que conteúdo HTML existente nos dados seja inserido diretamente na estrutura da página.

### 📊 Validação e Tratamento dos Dados

O dataset é processado antes de ser utilizado pela aplicação, incluindo:

- Remoção de colunas desnecessárias;
- Eliminação de registos duplicados;
- Normalização de texto;
- Conversão e validação do ano de lançamento;
- Tratamento de valores ausentes;
- Limpeza de conteúdo HTML presente nos dados.

Este tratamento reduz a possibilidade de dados inconsistentes ou inesperados afetarem o funcionamento da aplicação.

### 📁 Gestão de Ficheiros

A aplicação verifica a existência do dataset antes de tentar carregá-lo. Caso o ficheiro não esteja disponível, é apresentada uma mensagem informativa ao utilizador em vez de expor um erro técnico da aplicação.

As dependências utilizadas encontram-se definidas no ficheiro `requirements.txt`, permitindo reproduzir o ambiente necessário para executar o projeto.

---

## 🏆 Resultado

O projeto foi desenvolvido como **Projeto Final do curso de Programação em Python da Master.D**, tendo como objetivo a construção de um motor de pesquisa para exploração dos 1000 melhores filmes do IMDb.

Ao longo do desenvolvimento foram aplicados conhecimentos de programação em Python, importação, limpeza e tratamento de dados com `pandas`, pesquisa aproximada com `rapidfuzz` e desenvolvimento de uma interface web interativa com Streamlit.

**Classificação Final:** 🏆 *Em Breve*

---

## ✍️ Autor

**Bruno Pinto**
*Formação em Programação em Python*
Master.D
2026

---

## 📄 Licença e Aviso Legal

Este projeto foi desenvolvido exclusivamente para **fins académicos e de avaliação**, no âmbito do curso de **Programação em Python da Master.D**.

O código desenvolvido neste projeto é disponibilizado para fins educativos e de demonstração de conhecimentos de programação em Python, manipulação de dados e desenvolvimento de aplicações com Streamlit.

O dataset utilizado contém informações relativas a filmes provenientes do ranking dos 1000 melhores filmes do IMDb. Os dados e respetivos direitos associados permanecem propriedade dos seus autores e/ou das respetivas entidades detentoras.

Este projeto não possui qualquer afiliação oficial, parceria ou associação com o **IMDb**.