"""Olha a estrutura de alguns sites de imobiliárias (teste)."""
import re, sys
sys.path.insert(0, "scripts")
import atualizar as base
SITES = {
 "Lopes": "https://www.lopes.com.br/busca/venda/br/sp/sao-paulo/casa",
 "Nuroa": "https://www.nuroa.com.br/venda/casa-sao-paulo",
 "Marengo": "https://www.marengoimoveis.com.br/",
 "Vitoria": "https://www.vitoriaimoveis.com.br/",
 "Pantera": "https://panteraimoveis.com.br/",
 "Jac": "https://jacimoveis.com.br/",
 "Belleville": "https://www.bellevilleimoveis.com.br/",
 "MGF": "https://www.mgfimoveis.com.br/",
}
for nome, url in SITES.items():
    final, h = base.baixar(url)
    print("=====", nome, final, len(h))
    print("title:", (re.search(r"<title>(.*?)</title>", h, re.S) or [None, ""])[1].strip()[:100])
    links = list(dict.fromkeys(re.findall(r'href="([^"#]*(?:imovel|casa|venda)[^"#]*\d[^"#]*)"', h)))
    print("links:", len(links), links[:6])
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
    print("ldjson:", (m.group(1)[:300] if m else None))
    p = re.search(r".{120}R\$\s?[\d.]{6,}.{80}", h, re.S)
    print("preco ctx:", re.sub(r"\s+", " ", p.group(0)) if p else None)
    n = re.search(r'__NEXT_DATA__[^>]*>(.{0,300})', h, re.S)
    print("next:", n.group(1)[:300] if n else None)
