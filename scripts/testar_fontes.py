"""Testa, a partir do servidor do GitHub, quais portais e imobiliárias abrem para leitura automática."""
import re, urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
URLS = """
https://www.quintoandar.com.br/comprar/imovel/santo-andre-sp-brasil/casa
https://loft.com.br/venda/casas/sp/santo-andre
https://imoveis.mercadolivre.com.br/casas/venda/sao-paulo/santo-andre/
https://www.zapimoveis.com.br/venda/casas/sp+santo-andre/2-quartos/
https://www.vivareal.com.br/venda/sp/santo-andre/casa_residencial/2-quartos/
https://www.olx.com.br/imoveis/venda/casas/2-quartos/estado-sp/sao-paulo-e-regiao/santo-andre
https://www.imovelweb.com.br/casas-venda-santo-andre-sp-2-quartos.html
https://www.wimoveis.com.br/venda/casas/sp/santo-andre
https://www.lopes.com.br/busca/venda/br/sp/santo-andre/tipo/casa-terrea
https://www.nuroa.com.br/venda/casa-terrea-santo-andre
https://imoveis.trovit.com.br/casa-terrea-santo-andre
https://imoveis.mitula.com.br/imoveis/casas-santo-andre
https://www.casamineira.com.br/venda/casa/santo-andre_sp
https://www.dreamcasa.com.br/casas-a-venda-em-santo-andre-sp
https://www.imoveisjordao.com.br/imoveis/a-venda/casa/maua
https://www.bellvilleimoveis.com.br/casa/a-venda/maua-sp/2-quartos
https://panteraimoveis.com.br/venda/casa/santo-andre/
https://jacimoveis.com.br/p-casa-venda-santo_andre.html
https://www.pinotti.com.br/imoveis/a-venda/sao-bernardo-do-campo
https://www.tandeliimoveis.com.br/imobiliaria/venda/santo-andre-sp/casa-sobrado/imoveis/10001
https://www.imovelbrasil.net/casas/venda/sp/santo-andre/0-860000/
https://www.pedrodelima.com.br/casas/venda/sp/sao-paulo/vila-matilde/
https://www.mouraimoveissp.com.br/
https://www.marengoimoveis.com.br/venda/casa-terrea/sao-paulo-sp/bairro-vila-formosa
https://www.andregraciutti.com.br/imovel/venda/casa-terrea/santo-andre
https://www.mgfimoveis.com.br/venda/casa/sp-sao-bernardo-do-campo-ferrazopolis
https://www.trevisanabcimoveis.com.br/imoveis/a-venda/casa/sao-bernardo-do-campo/planalto
https://www.shangrilar.com.br/imoveis/a-venda/casa/sao-bernardo-do-campo/pauliceia
https://www.imobiliariavitoria.com.br/casa-terrea/venda/sp/sao-bernardo-do-campo/7
https://lisaimoveis.com.br/p-casa-bairro_pauliceia.html
https://www.nestoria.com.br/sao-bernardo-do-campo/casas/venda
https://www.chavesnamao.com.br/casas-a-venda/sp-santo-andre/
https://www.abcimovel.com.br/imoveis/casas/venda/santo-andre/grande-abc/sao-paulo/
""".split()

for u in URLS:
    try:
        req = urllib.request.Request(u, headers={"User-Agent": UA, "Accept-Language": "pt-BR"})
        with urllib.request.urlopen(req, timeout=25) as r:
            h = r.read(1_500_000).decode("utf-8", "ignore")
            print(f"{r.status:>4} {len(h):>8} precos={len(re.findall(r'R\$\s?\d', h)):>4} ldjson={h.count('ld+json'):>2}  {u}")
    except Exception as e:
        print(f"ERRO {str(e)[:60]:<60} {u}")
