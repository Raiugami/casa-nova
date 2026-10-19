# Casa Nova

Casas térreas à venda com 2 quartos ou mais, até R$ 360 mil, em São Paulo, Santo André, Mauá e São Bernardo do Campo.

- `index.html` é o site (GitHub Pages) e lê `imoveis.json`.
- `scripts/atualizar.py` coleta os anúncios do ABC Imóvel, SP Imóvel e ZL Imóvel e regrava `imoveis.json`.
- `.github/workflows/atualizar.yml` roda o script todo dia e salva o resultado.

Anúncios indisponíveis, parados há mais de um ano ou que citam dívida, financiamento, retomado, sobrado, geminada ou condomínio são removidos automaticamente.
