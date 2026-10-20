"""Procura páginas de busca de casas em imobiliárias do ABC e na Lopes (teste)."""
import re, sys, html
sys.path.insert(0, "scripts")
import atualizar as base
SITES = {
 "Pantera": "https://panteraimoveis.com.br/",
 "Marengo": "https://www.marengoimoveis.com.br/",
 "Jac": "https://www.jacimoveis.com.br/",
 "Lopes": "https://www.lopes.com.br/busca/venda/br/sp/sao-paulo/casa",
}
for nome, url in SITES.items():
    final, h = base.baixar(url)
    print("=====", nome, final, len(h))
    ls = list(dict.fromkeys(html.unescape(x) for x in re.findall(r'href="([^"#]+)"', h)))
    busca = [l for l in ls if re.search(r"casa|venda|comprar|busca", l, re.I) and not re.search(r"\d{4,}", l)]
    print("busca:", busca[:14])
    imo = [l for l in ls if re.search(r"/imovel/|/p-", l)]
    print("exemplos:", imo[:4])
    if nome == "Lopes":
        for m in list(re.finditer(r'"(?:id|slug|url|price|preco|salePrice|isReo|reo)"\s*:\s*"?[^,"}]{1,60}', h))[:25]:
            print("  ", m.group(0)[:90])
        n = re.search(r"__NEXT_DATA__[^>]*>(.{0,500})", h, re.S)
        print("next:", n.group(1)[:500] if n else None)
