# 🏁 F1 Analyst - Dashboard de Dados de Fórmula 1

Este projeto é um dashboard completo de análise de dados de corridas da Fórmula 1, desenvolvido em Python utilizando FastF1, Dash e Plotly.\
O sistema permite visualizar e explorar informações detalhadas sobre sessões, pilotos, equipes, pneus e desempenho nas principais corridas da temporada.

## 🚦 Funcionalidades

- Filtros dinâmicos de ano, GP, sessão, pilotos e compostos de pneus
- Gráficos interativos com Plotly
- Análises de melhor volta, stints por piloto, heatmap de setores, ritmo comparativo entre pilotos, pit windows, força das equipes (corrida e qualify)
- Interface responsiva e intuitiva
- Atualização em tempo real dos dados via FastF1

## 💻 Tecnologias Utilizadas

- [Python 3.10+](https://www.python.org/)
- [Dash](https://dash.plotly.com/)
- [Plotly](https://plotly.com/python/)
- [FastF1](https://theoehrly.github.io/Fast-F1/)
- [Pandas](https://pandas.pydata.org/)
- [React-Select CSS customizado]
- [Bootstrap (opcional para estilos adicionais)]

## ⚡ Como rodar localmente

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/ryanlbroilo/F1-Analyst.git
   cd F1-Analyst
   ```

2. **Crie um ambiente virtual e instale as dependências:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Crie a pasta de cache do FastF1 (caso não exista):**

   ```bash
   mkdir f1cache
   ```

4. **Rode a aplicação:**

   ```bash
   python app.py
   ```

5. **Acesse em:**\
   [http://localhost:8050](http://localhost:8050)

## 📁 Estrutura do Projeto

```
F1-Analyst/
├── app.py
├── requirements.txt
├── assets/
│   └── style.css
└── README.md
```

## 🤝 Contribuições

Sinta-se à vontade para abrir issues, enviar sugestões ou contribuir com melhorias!

## 📢 Créditos

- Desenvolvido por Ryan L Broilo
- Dados e API via [FastF1](https://theoehrly.github.io/Fast-F1/)
- Visualizações com [Dash](https://dash.plotly.com/) & [Plotly](https://plotly.com/python/)

---

⭐️ Se curtiu o projeto, deixe uma estrela!\
Dúvidas ou sugestões? Me chama no [LinkedIn](https://www.linkedin.com/in/ryan-lizze-broilo-737102209/).

