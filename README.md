# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# Nome do projeto

## Grupo 98

## 👨‍🎓 Integrantes: 
- <a href="https://www.linkedin.com/company/inova-fusca">Eduardo Venancio Leite</a> 
- <a href="https://www.linkedin.com/company/inova-fusca">Francisco José Bittencourt Corrêa</a>
- <a href="https://www.linkedin.com/company/inova-fusca">Jullyana de Azevedo Rodrigues</a>
- <a href="https://www.linkedin.com/in/kaiquecadimiel/">Kaique Cadimiel Amasio de Souza</a>

## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="https://www.linkedin.com/company/inova-fusca">Nicolly Candida Rodrigues de Souza</a>
### Coordenador(a)
- <a href="https://www.linkedin.com/company/inova-fusca">ANDRÉ GODOI CHIOVATO</a>



## 📜 Descrição FarmTech Solutions — Monitoramento de Colheita de Cana-de-Açúcar
 
Sistema de telemetria para colhedoras mecanizadas que coleta parâmetros operacionais em tempo real, calcula a perda de produção e gera diagnósticos com ações corretivas baseadas em padrões agronômicos reais.
 
## Como funciona
 
O operador informa os dados da colhedora (velocidade, rotação do extrator, altura de corte e tonelagem esperada vs. realizada). O sistema calcula o percentual de perda e compara cada parâmetro contra as faixas ideais definidas pela **Embrapa Agroenergia** e pelo **CONSECANA-SP**.
 
O diagnóstico é proporcional à perda encontrada — quanto maior o desvio, mais severa e específica é a recomendação. O resultado é exibido no terminal com o status da operação, os parâmetros fora de faixa, a estimativa de prejuízo financeiro e um plano de ação ordenado por prioridade.
 
Cada análise é persistida no **Oracle Database** e salva localmente em **JSON** para rastreabilidade.
 
---
 
## Stack
 
| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.10+ |
| Banco de dados | Oracle XE (via `oracledb`) |
| Log local | JSON (stdlib) |
| Testes | `pytest` |
 
---
 
## Parâmetros monitorados
 
| Parâmetro | Faixa ideal | Impacto do desvio |
|---|---|---|
| Velocidade | 3,5 – 5,5 km/h | Acima: fragmenta colmos. Abaixo: reduz capacidade. |
| Rotação do extrator | 600 – 800 RPM | Acima: lança cana com a palha. Abaixo: excesso de palha na carga. |
| Altura de corte | 2 – 5 cm | Acima: perda de sacarose e dano à soqueira. Abaixo: destrói gemas de rebrota. |
 
---
 
## Níveis de severidade
 
```
< 3%   ✅  OTIMIZADO   — Dentro do padrão. Manter configuração.
3–8%   ⚠️  ATENÇÃO     — Ajustes preventivos recomendados.
8–15%  🔶  ELEVADO     — Intervenção operacional necessária.
15–25% 🔴  CRÍTICO     — Parar e recalibrar. Checar desgaste de facas.
> 25%  🚨  EMERGÊNCIA  — Suspender operação para manutenção.
```


## 📁 Estrutura de pastas

Dentre os arquivos e pastas presentes na raiz do projeto, definem-se:

- <b>.github</b>: Nesta pasta ficarão os arquivos de configuração específicos do GitHub que ajudam a gerenciar e automatizar processos no repositório.

- <b>assets</b>: aqui estão os arquivos relacionados a elementos não-estruturados deste repositório, como imagens.

- <b>config</b>: Posicione aqui arquivos de configuração que são usados para definir parâmetros e ajustes do projeto.

- <b>document</b>: aqui estão todos os documentos do projeto que as atividades poderão pedir. Na subpasta "other", adicione documentos complementares e menos importantes.

- <b>scripts</b>: Posicione aqui scripts auxiliares para tarefas específicas do seu projeto. Exemplo: deploy, migrações de banco de dados, backups.

- <b>src</b>: Todo o código fonte criado para o desenvolvimento do projeto ao longo das 7 fases.

- <b>README.md</b>: arquivo que serve como guia e explicação geral sobre o projeto (o mesmo que você está lendo agora).

## 🔧 Como executar o código

### Pré-requisitos
- **Python 3.8+**: Certifique-se de ter o Python instalado em sua máquina
- **pip**: Gerenciador de pacotes do Python
- **Docker Desktop**: Para executar o banco de dados Oracle (recomendado)

### Instalação

1. **Clone o repositório**
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd cap-6-python-e-alem
   ```

2. **Crie um ambiente virtual** (recomendado)
   ```bash
   python -m venv venv
   # No macOS/Linux:
   source venv/bin/activate
   # No Windows:
   # venv\Scripts\activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

## 🐳 Docker & Banco de Dados

Para garantir a portabilidade e facilitar a avaliação, o projeto utiliza Docker para o banco de dados Oracle. Como o desenvolvimento foi realizado em um Mac M4 (ARM64), a imagem é executada via emulação Rosetta.

### Inicialização do Banco de Dados

Certifique-se de que o Docker Desktop está rodando e execute:

```bash
docker run -d --name oracle-farmtech \
  --platform linux/amd64 \
  -p 1521:1521 \
  -e ORACLE_PASSWORD=admin123 \
  gvenzl/oracle-xe:slim-faststart
```

### Criação das Tabelas

Após o container exibir o status `(healthy)`, acesse o SQLPlus para criar a estrutura:

```bash
# Acesso ao prompt SQL
docker exec -it oracle-farmtech sqlplus system/admin123@localhost:1521/xe
```

Execute o script DDL:

```sql
CREATE TABLE colhedoras (
    id_maquina VARCHAR2(20) PRIMARY KEY,
    modelo VARCHAR2(50) NOT NULL,
    vel_max_ideal NUMBER(4,2),
    rot_extrator_ideal NUMBER(4),
    altura_corte_ideal NUMBER(4,2)
);

CREATE TABLE registros_colheita (
    id_registro NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    id_maquina VARCHAR2(20) NOT NULL,
    velocidade_real NUMBER(4,2),
    rotacao_real NUMBER(4),
    altura_real NUMBER(4,2),
    ton_esperada NUMBER(10,2),
    ton_realizada NUMBER(10,2),
    perda_percentual NUMBER(5,2),
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_maquina FOREIGN KEY (id_maquina) REFERENCES colhedoras(id_maquina)
);

-- Inserção de máquina para teste
INSERT INTO colhedoras VALUES ('JD-7000', 'John Deere S-Series', 4.5, 800, 3.0);
COMMIT;
```

### Credenciais de Conexão

| Configuração | Valor |
|---|---|
| **Usuário** | `system` |
| **Senha** | `admin123` |
| **DSN** | `localhost:1521/xe` |
| **Driver** | `oracledb` (modo Thin) |

## 🚀 Executando o Projeto

Para executar o aplicativo principal:
```bash
python src/main.py
```

Para executar testes de banco de dados:
```bash
python src/teste_db.py
```

## 📚 Estrutura de Módulos

- **src/main.py**: Ponto de entrada da aplicação
- **src/config.py**: Configurações da aplicação
- **src/database.py**: Gerenciamento do banco de dados
- **src/core_logic.py**: Lógica principal do projeto
- **src/file_manager.py**: Gerenciamento de arquivos
- **src/utils.py**: Funções utilitárias
- **src/reports.py**: Geração de relatórios


## 🗃 Histórico de lançamentos

* 0.5.0 - XX/XX/2024
    * 
* 0.4.0 - XX/XX/2024
    * 
* 0.3.0 - XX/XX/2024
    * 
* 0.2.0 - XX/XX/2024
    * 
* 0.1.0 - XX/XX/2024
    *

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>


