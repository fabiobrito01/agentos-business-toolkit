# AgentOS Business Toolkit

Kit offline e portátil para pequenos negócios registrarem clientes e vendas em SQLite, sem mensalidade ou nuvem obrigatória.

```bash
python business.py cliente "Cliente Exemplo" --telefone "(00) 00000-0000"
python business.py venda 1 "Serviço" 150.00
python business.py resumo
```

Os comandos usam parâmetros SQL seguros. Por padrão, os dados ficam em `~/.agentos_business.db`. Projeto AgentOStudio · Licença MIT.
