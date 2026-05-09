# 🗝️ Quadro de Chaves — Key Management Board

Sistema de gerenciamento de chaves desenvolvido com **Python** e **Tkinter**. Permite controlar a retirada e devolução de chaves, registrar eventos e gerar relatórios — tudo com autenticação de usuário para rastreabilidade completa.

Projeto desenvolvido para uso interno com foco em praticidade e rastreabilidade no controle físico de chaves.

---

## ✨ Funcionalidades

- **Login de usuário** — acesso restrito a usuários autorizados, garantindo rastreabilidade de quem interagiu com cada chave
- **Gerenciamento de chaves** — registra retirada e devolução, exibindo responsável e horário
- **Histórico de eventos** — todos os eventos ficam registrados para consulta e auditoria
- **Geração de relatórios** — relatórios detalhados de retiradas e devoluções com identificação do operador
- **Reset de estado** — redefine todas as chaves para disponível quando necessário

---

## 🗄️ Banco de Dados

O sistema utiliza **SQLite** para armazenar as informações de chaves e eventos. O banco de dados (`chaves.db`) é criado automaticamente na primeira execução — nenhuma configuração manual é necessária.

---

## 🚀 Como Executar

**1. Pré-requisitos**

Certifique-se de ter o Python 3 instalado. O Tkinter já vem incluído no Python para Windows. No Linux, instale com:

```bash
sudo apt-get install python3-tk
```

**2. Clone o repositório**

```bash
git clone https://github.com/ReehCitelli/craviculario.git
cd craviculario
```

**3. Execute o programa**

```bash
python chaves.py
```

**4. Faça login**

Use um dos usuários cadastrados para acessar o sistema. A senha padrão é igual ao nome do usuário.

| Usuário | Senha |
|---|---|
| Usuario1 | Usuario1 |
| Usuario2 | Usuario2 |
| Usuario3 | Usuario3 |
| Usuario4 | Usuario4 |

> Para personalizar os usuários, edite a variável `USUARIOS_AUTORIZADOS` no arquivo `chaves.py`.

---

## 📁 Estrutura do Projeto

```
📦 craviculario
 ┣ 📄 chaves.py        ← script principal
 ┣ 📄 chaves.db        ← banco de dados SQLite (gerado automaticamente)
 ┗ 📄 README.md
```

---

## 🛠️ Tecnologias

- Python 3
- Tkinter — interface gráfica desktop
- SQLite — banco de dados local

---

## 📝 Observação

Os usuários e funcionalidades do sistema podem ser facilmente adaptados para outras necessidades de controle de acesso a itens físicos.

---

> Desenvolvido por [@ReehCitelli](https://github.com/ReehCitelli) · Jornada de transição para Ciência de Dados 🚀
