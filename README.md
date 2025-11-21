# PaceHub

Sistema de gerenciamento de eventos de corrida desenvolvido em Python seguindo os princípios de arquitetura UML (Model-View-Controller).

## 📋 Descrição

O PaceHub é uma aplicação desktop para gerenciamento completo de eventos de corrida, permitindo que organizadores criem e gerenciem eventos, enquanto atletas podem se inscrever e ter seus resultados registrados. O sistema implementa validações robustas, classificação automática de resultados e gerenciamento de kits de corrida.

## 🏗️ Arquitetura

O projeto segue a arquitetura MVC (Model-View-Controller) com separação clara de responsabilidades:

- **Entidade** (`entidade/`): Classes que representam as entidades do domínio
- **Persistência** (`persistencia/`): Data Access Objects (DAOs) para operações de banco de dados
- **Controle** (`controle/`): Controladores que implementam a lógica de negócio
- **Limite** (`limite/`): Interfaces gráficas (telas) usando FreeSimpleGUI

## 🗄️ Banco de Dados

O sistema utiliza SQLite como banco de dados relacional, com as seguintes tabelas principais:

- `usuarios`: Armazena atletas e organizadores
- `Eventos`: Informações dos eventos de corrida
- `inscricoes`: Relacionamento entre atletas e eventos
- `KitsDeCorrida`: Kits disponíveis para cada evento
- `Resultados`: Resultados dos atletas nos eventos

## ✨ Casos de Uso Implementados

### 1. Gestão de Usuários

#### 1.1. Cadastro de Atleta
- Cadastro de novos atletas no sistema
- Validação de CPF (formato e dígitos verificadores)
- Validação de email
- Criptografia de senha usando bcrypt
- Campos obrigatórios: Nome, CPF, Email, Data de Nascimento, Gênero, Senha
- Suporte para atletas PCD (Pessoa com Deficiência)

#### 1.2. Cadastro de Organizador
- Cadastro de organizadores de eventos
- Validação de CPF e email
- Criptografia de senha

#### 1.3. Login no Sistema
- Autenticação por CPF e senha
- Redirecionamento para painel específico (Atleta ou Organizador)
- Validação de credenciais

#### 1.4. Listagem de Usuários
- Listagem de todos os atletas cadastrados
- Listagem de todos os organizadores cadastrados

### 2. Gestão de Eventos

#### 2.1. Criar Evento
- Criação de novos eventos de corrida
- Campos: Nome, Data, Distância, Local de Largada, Tempo de Corte, Data Limite para Crédito
- Associação automática ao organizador logado
- Validação de datas

#### 2.2. Editar Evento
- Edição de eventos existentes
- Atualização de informações do evento
- Validação de dados

#### 2.3. Visualizar Eventos
- Listagem de eventos do organizador
- Exibição de informações: Nome, Data, Número de Inscritos, Status
- Status automático baseado na data do evento (Concluído/Futuro)

### 3. Gestão de Kits de Corrida

#### 3.1. Cadastrar Kits
- Criação de kits de corrida para eventos
- Campos: Nome, Descrição, Valor
- Múltiplos kits por evento

#### 3.2. Gerenciar Entrega de Kits
- Busca de inscrições por CPF ou nome do atleta
- Atualização do status de entrega do kit (Entregue/Não Entregue)
- Visualização de informações da inscrição

### 4. Gestão de Inscrições

#### 4.1. Inscrição de Atletas
- Inscrição de atletas em eventos
- Seleção de kit de corrida
- Validação de atleta existente
- Status de inscrição (Pendente/Paga)

#### 4.2. Consultar Inscrições
- Busca de inscrições por atleta
- Visualização de detalhes da inscrição
- Informações do evento e kit selecionado

### 5. Importação de Resultados

#### 5.1. Importar Resultados via CSV
- Importação em lote de resultados de atletas
- Formato CSV: `CPF,Tempo` (sem cabeçalho)
- Validações implementadas:
  - **CPF inválido**: Validação de formato e dígitos verificadores
  - **Atleta não cadastrado**: Verificação de existência no banco
  - **Atleta não inscrito**: Validação de inscrição no evento
  - **Tempo inválido**: Validação de formato HH:MM:SS
  - **Formato de arquivo**: Validação de estrutura do CSV
- Relatório detalhado de erros linha por linha
- Substituição automática de resultados anteriores

#### 5.2. Cálculo Automático de Classificações
- **Classificação Geral (RN06)**: Top 5 de cada gênero (Masculino/Feminino)
- **Classificação por Categoria (RN07)**: 
  - Júnior (até 17 anos)
  - Adulto (18-49 anos)
  - Master (50+ anos)
  - PCD (competem separadamente)
- Cálculo baseado na idade do atleta em 31/12 do ano do evento
- Ordenação automática por tempo

#### 5.3. Validação de Evento Concluído
- Importação permitida apenas para eventos com data no passado
- Validação automática do status do evento

### 6. Cálculo de Categorias

#### 6.1. Categoria por Idade
- Cálculo automático da categoria do atleta
- Baseado na idade em 31/12 do ano do evento
- Regras:
  - **Júnior**: ≤ 17 anos
  - **Adulto**: 18-49 anos
  - **Master**: ≥ 50 anos
  - **PCD**: Sempre categoria PCD, independente da idade

## 🛠️ Tecnologias Utilizadas

- **Python 3.13**
- **FreeSimpleGUI**: Interface gráfica
- **SQLite**: Banco de dados
- **bcrypt**: Criptografia de senhas
- **csv**: Processamento de arquivos CSV

## 📦 Estrutura de Arquivos

```
PaceHub_main/
├── controle/              # Controladores (lógica de negócio)
│   ├── controlador_atleta.py
│   ├── controlador_evento.py
│   ├── controlador_importacao.py
│   ├── controlador_inscricao.py
│   ├── controlador_organizador.py
│   └── controlador_sistema.py
├── entidade/              # Entidades do domínio
│   ├── atleta.py
│   ├── evento.py
│   ├── inscricao.py
│   ├── kit_de_corrida.py
│   ├── organizador.py
│   ├── resultado.py
│   └── usuario.py
├── limite/                # Interfaces gráficas
│   ├── tela_cadastro.py
│   ├── tela_evento.py
│   ├── tela_importar_resultados.py
│   ├── tela_inscricao.py
│   ├── tela_organizador.py
│   └── tela_principal.py
├── persistencia/          # Data Access Objects
│   ├── evento_dao.py
│   ├── inscricao_dao.py
│   ├── resultado_dao.py
│   └── usuario_dao.py
├── csv/                   # Arquivos CSV de teste
├── cria_banco.py          # Script de criação do banco
├── popula_banco.py        # Script de população inicial
├── gerar_evento_teste.py  # Script para gerar dados de teste
└── main.py                # Ponto de entrada da aplicação
```

## 🚀 Como Executar

### Pré-requisitos
- Python 3.13 ou superior
- Dependências: `FreeSimpleGUI`, `bcrypt`

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/ldavila43/PaceHub.git
cd PaceHub
```

2. Instale as dependências:
```bash
pip install FreeSimpleGUI bcrypt
```

3. Crie o banco de dados:
```bash
python cria_banco.py
```

4. Popule o banco com dados iniciais (opcional):
```bash
python popula_banco.py
```

5. Execute a aplicação:
```bash
python main.py
```

## 🧪 Testes

O projeto inclui scripts para geração de dados de teste:

- `gerar_evento_teste.py`: Gera evento, inscrições e arquivos CSV de teste
- Arquivos CSV de teste com diferentes tipos de erros para validação:
  - `resultados_teste.csv`: CSV válido
  - `resultados_erro_cpf_invalido.csv`: CPFs inválidos
  - `resultados_erro_atleta_nao_cadastrado.csv`: Atletas não cadastrados
  - `resultados_erro_tempo_nao_informado.csv`: Tempos vazios
  - `resultados_erro_tempo_invalido.csv`: Tempos em formato inválido
  - `resultados_erro_formato_invalido.csv`: Formato de arquivo incorreto
  - `resultados_erro_atleta_nao_inscrito.csv`: Atletas não inscritos
  - `resultados_erro_multiplos_erros.csv`: Múltiplos erros misturados

## 📝 Regras de Negócio Implementadas

- **RN04**: Categoria do atleta baseada na idade em 31/12 do ano do evento
- **RN06**: Classificação Geral = Top 5 de cada gênero
- **RN07**: Classificação por categoria para demais atletas
- **Validação de CPF**: Formato e dígitos verificadores
- **Validação de Evento**: Importação apenas para eventos concluídos
- **Validação de Inscrição**: Atleta deve estar inscrito para ter resultado importado

## 👥 Autores

- Lucas Dutra de Ávila

## 📄 Licença

Este projeto está sob licença MIT.

## 🔗 Repositório

[GitHub - PaceHub](https://github.com/ldavila43/PaceHub)

