"""Coleta casas térreas dos portais ABC Imóvel, SP Imóvel e ZL Imóvel e grava imoveis.json.

Só usa a biblioteca padrão. Uso: python scripts/atualizar.py
"""
import html, json, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date

ARQ = "imoveis.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
PRECO_MAX = 360_000
MAX_PAGINAS = 45

# (portal, base, cidade)
BUSCAS = [
    ("ABC Imóvel", "https://www.abcimovel.com.br", "/imoveis/casas/venda/santo-andre/grande-abc/sao-paulo/"),
    ("ABC Imóvel", "https://www.abcimovel.com.br", "/imoveis/casas/venda/maua/grande-abc/sao-paulo/"),
    ("ABC Imóvel", "https://www.abcimovel.com.br", "/imoveis/casas/venda/sao-bernardo-do-campo/grande-abc/sao-paulo/"),
    ("SP Imóvel", "https://www.spimovel.com.br", "/imoveis/casas/venda/santo-andre/grande-abc/sao-paulo/"),
    ("SP Imóvel", "https://www.spimovel.com.br", "/imoveis/casas/venda/maua/grande-abc/sao-paulo/"),
    ("SP Imóvel", "https://www.spimovel.com.br", "/imoveis/casas/venda/sao-bernardo-do-campo/grande-abc/sao-paulo/"),
    ("SP Imóvel", "https://www.spimovel.com.br", "/imoveis/casas/venda/sao-paulo/"),
    ("ZL Imóvel", "https://www.zlimovel.com.br", "/imoveis/casas-terreas/venda/zona-leste/sao-paulo/"),
]

CIDADES = {"santo-andre": "Santo André", "maua": "Mauá", "sao-bernardo-do-campo": "São Bernardo do Campo", "sao-paulo": "São Paulo"}
# fragmentos de slug para achar a cidade (do mais específico ao mais geral)
CIDADE_SLUG = [("sao-bernardo-do-campo", "São Bernardo do Campo"), ("santo-andre", "Santo André"), ("maua", "Mauá"), ("sao-paulo", "São Paulo")]

BLOQUEIO = re.compile(
    r"transfer[eê]ncia de d[ií]vida|assum(?:ir|ir a|ção de) (?:a )?d[ií]vida|financiamento (?:em andamento|ativo|a quitar)|"
    r"saldo devedor|retomad|leil[aã]o|d[ií]vida|aliena[cç][aã]o fiduci[aá]ria|repasse de financiamento|caixa econ[oô]mica retomado|"
    r"sobrado|geminad|condom[ií]nio fechado|em condom[ií]nio|casa de vila|vila fechada|assobradad|terreno|lote",
    re.I,
)
# bairros periféricos ou com morro. A lista é uma avaliação aproximada e pode ser ajustada.
ATENCAO = {
    "Santo André": ["jardim santo andre", "vila suica", "jardim santo alberto", "parque miami", "cidade sao jorge", "parque andreense", "jardim santo alberto", "recreio da borda do campo", "vila luzita", "jardim alzira franco", "jardim cristiane", "vila sao pedro", "parque novo oratorio", "jardim ana maria", "jardim sao caetano"],
    "Mauá": ["jardim itapark velho", "jardim zaira", "jardim cruzeiro", "parque sao vicente", "vila magini", "jardim maua", "vila carlina", "jardim oratorio", "jardim primavera", "parque capuava", "jardim silvia maria", "jardim sonia maria"],
    "São Bernardo do Campo": ["alvarenga", "batistini", "montanhao", "jardim silvina", "jordanopolis", "taboao", "riacho grande", "jardim thelma", "rudge ramos"],
    "São Paulo": ["vila rica", "jardim casa pintada", "itaquera", "guaianases", "sao miguel", "cidade tiradentes", "ermelino", "jardim helena", "lajeado", "itaim paulista", "cidade lider", "jose bonifacio", "sapopemba", "burgo paulista", "vila nhocune", "jardim sao paulo"],
}
BOA = {
    "Santo André": ["vila guarani", "vila palmares", "vila lucinda", "vila guaraciaba", "jardim irene", "jardim bela vista", "vila metalurgica", "vila scarpelli", "vila pires", "parque oratorio", "jardim ocara", "jardim stella", "vila alpina", "vila eldizia", "vila vitoria", "campestre", "centro", "vila assuncao", "vila pires", "vila guiomar", "vila america", "casa branca", "santa maria", "bangu", "utinga", "vila humaita"],
    "Mauá": ["vila feital", "vila bocaina", "centro", "jardim pilar", "vila noemia", "vila assis brasil", "vila vitoria"],
    "São Bernardo do Campo": ["centro", "baeta neves", "jardim do mar", "vila baeta neves", "santa terezinha", "assuncao", "nova petropolis", "vila marlene", "ferrazopolis", "anchieta", "planalto", "paulicéia", "pauliceia"],
    "São Paulo": ["tatuape", "vila formosa", "ipiranga", "mooca", "vila prudente", "penha", "vila matilde", "vila carrao", "saude", "vila mariana", "parada inglesa", "santana", "tucuruvi", "vila maria", "agua rasa", "anália franco", "analia franco", "jabaquara", "sacoma"],
}


def baixar(url, tentativas=3):
    for t in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.geturl(), r.read(900_000).decode("utf-8", "ignore")
        except Exception:
            time.sleep(1.5 * (t + 1))
    return url, ""


def sem_acento(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


def links_da_busca(item):
    portal, base, caminho = item
    achados = {}
    vazias = 0
    for n in range(1, MAX_PAGINAS + 1):
        final, h = baixar(f"{base}{caminho}?pageNumber={n}")
        if "indisponivel=true" in final:
            break
        novos = re.findall(r'href="(/imovel/casa-terrea-venda-[^"]+/(\d+)/)"', h)
        antes = len(achados)
        for url, pid in novos:
            achados[pid] = (portal, base + url)
        if len(achados) == antes:
            vazias += 1
            if vazias >= 2:
                break
        else:
            vazias = 0
    return achados


def candidato_por_slug(url):
    """Lê tipo, faixa de preço, quartos e cidade do próprio link do anúncio."""
    s = url.split("/imovel/")[1]
    m = re.match(r"casa-terrea-venda-(?:rs(\d+)|(\d+)(mil|milhoes)-ate-\d+(?:mil|milhoes)|\d+mil)-(\d+)quartos?", s)
    if not m:
        return None
    if m.group(1):
        if int(m.group(1)) > PRECO_MAX:
            return None
    elif m.group(2) and m.group(3) == "mil" and int(m.group(2)) >= 360:
        return None
    elif m.group(3) == "milhoes":
        return None
    return int(m.group(4)) >= 2


def detalhe(par):
    pid, (portal, url) = par
    final, h = baixar(url)
    if not h or "indisponivel=true" in final or f"/{pid}/" not in final:
        return None
    titulo = re.search(r"<title>(.*?)</title>", h, re.S)
    titulo = html.unescape(titulo.group(1)).strip() if titulo else ""
    preco = re.search(r"R\$\s?([\d\.]+),\d\d", titulo)
    if not preco:
        return None
    preco = int(preco.group(1).replace(".", ""))
    if preco > PRECO_MAX:
        return None
    desc = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]*)"', h)
    desc = html.unescape(desc.group(1)) if desc else ""
    corpo = re.sub(r"<[^>]+>", " ", re.sub(r"(?s)<(script|style).*?</\1>", " ", h))
    corpo = html.unescape(re.sub(r"\s+", " ", corpo))
    # texto do anúncio: o trecho em torno da descrição do imóvel
    ini = corpo.lower().find("descri")
    texto = corpo[ini: ini + 2500] if ini >= 0 else desc
    if BLOQUEIO.search(titulo + " " + texto[:2500]):
        return None
    slug = final.split("/imovel/")[1]
    q = re.search(r"-(\d+)quartos?", slug)
    v = re.search(r"-(\d+)vagas?", slug)
    a = re.search(r"-(\d+)m2", slug)
    # título: "Casa Térrea, 2 Quartos à Venda, Bairro, Cidade, 100 m² por R$ ..."
    titulo = re.sub(r"\s+", " ", titulo)
    partes = [p.strip() for p in titulo.split(" por R$")[0].split(",")]
    partes = [p for p in partes if p and not re.fullmatch(r"[\d\.]+ ?m.?", p)]
    limpas = [re.sub(r"\s*à Venda\s*$", "", p) for p in partes]
    cidade = next((p for p in reversed(limpas) if p in CIDADES.values()), None)
    resto = [p for p in limpas if p != cidade and not re.search(r"quartos?$|^casa t", p, re.I)]
    if not cidade or not resto:
        return None
    bairro = resto[-1]
    bairro = re.sub(r"\s*\(Zona Leste\)", "", bairro)
    imgs = list(dict.fromkeys(re.findall(r'https://d31hw7dq38n1ek\.cloudfront\.net/Imagens/[^"\' )]*/Imovel/%s/[^"\' )]+\.jpe?g' % pid, h)))
    og = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', h)
    imagem = imgs[0] if imgs else (og.group(1) if og and "logos/" not in og.group(1) else None)
    atualizado = re.search(r"[Aa]tualizado em:?\s*(\d{2})/(\d{2})/(\d{4})", corpo)
    data_anuncio = f"{atualizado.group(3)}-{atualizado.group(2)}-{atualizado.group(1)}" if atualizado else None
    if data_anuncio and (date.today() - date.fromisoformat(data_anuncio)).days > 365:
        return None
    sb = sem_acento(bairro)
    loc = "media"
    if sb in ATENCAO.get(cidade, []):
        loc = "atencao"
    elif sb in BOA.get(cidade, []):
        loc = "boa"
    return {
        "id": f"{portal.split()[0].lower()}-{pid}",
        "cidade": cidade,
        "bairro": bairro,
        "preco": preco,
        "quartos": int(q.group(1)) if q else None,
        "vagas": int(v.group(1)) if v else None,
        "area": int(a.group(1)) if a else None,
        "tipo": "Térrea",
        "extras": (desc[:140] if desc else ""),
        "fonte": portal,
        "url": final,
        "link_direto": True,
        "anuncio_data": f"{atualizado.group(3)}-{atualizado.group(2)}-{atualizado.group(1)}" if atualizado else None,
        "imagem": imagem,
        "localizacao": loc,
        "nota_local": {"boa": "Bairro consolidado e bem servido.", "media": "Bairro residencial; confirme topografia e entorno.", "atencao": "Região periférica ou com ruas em morro."}[loc],
    }


def buscas_por_bairro(todos):
    """Monta buscas por bairro a partir dos bairros vistos nos links já coletados e da lista fixa."""
    cidade_pasta = {"Santo André": "santo-andre", "Mauá": "maua", "São Bernardo do Campo": "sao-bernardo-do-campo"}
    bairros = {c: set() for c in cidade_pasta}
    for portal, url in todos.values():
        slug = url.split("/imovel/")[1]
        for nome, pasta in cidade_pasta.items():
            m = re.search(r"\dm2-(.+?)-%s-" % pasta, slug) or re.search(r"quartos?-(?:\d+vagas?-)?(.+?)-%s-" % pasta, slug)
            if m:
                bairros[nome].add(m.group(1))
    for nome, lista in {**{c: [sem_acento(b).replace(" ", "-") for b in BOA[c] + ATENCAO[c]] for c in cidade_pasta}}.items():
        bairros[nome].update(lista)
    out = []
    for nome, pasta in cidade_pasta.items():
        for b in sorted(bairros[nome]):
            out.append(("ABC Imóvel", "https://www.abcimovel.com.br", f"/imoveis/casas/venda/{b}/{pasta}/grande-abc/sao-paulo/"))
            out.append(("SP Imóvel", "https://www.spimovel.com.br", f"/imoveis/casas/venda/{b}/{pasta}/grande-abc/sao-paulo/"))
    zl = sorted({sem_acento(b).replace(" ", "-") for b in BOA["São Paulo"] + ATENCAO["São Paulo"]})
    for b in zl:
        out.append(("ZL Imóvel", "https://www.zlimovel.com.br", f"/imoveis/casas/venda/{b}/zona-leste/sao-paulo/"))
        out.append(("SP Imóvel", "https://www.spimovel.com.br", f"/imoveis/casas/venda/{b}/sao-paulo/"))
    return out


# ---------------------------------------------------------------- Chaves na Mão
CHAVES = "https://www.chavesnamao.com.br"
CHAVES_CIDADES = {"sp-santo-andre": "Santo André", "sp-maua": "Mauá", "sp-sao-bernardo-do-campo": "São Bernardo do Campo", "sp-sao-paulo": "São Paulo"}
CHAVES_LINK = re.compile(r'/imovel/casa-a-venda-(\d+)-quartos?[a-z0-9-]*?-(?:(\d+)m2-)?RS(\d+)/id-(\d+)/')


def chaves_links(caminho):
    achados = {}
    for n in range(1, MAX_PAGINAS + 1):
        final, h = baixar(f"{CHAVES}{caminho}?pg={n}")
        novos = 0
        for m in re.finditer(r'(/imovel/casa-a-venda-[A-Za-z0-9-]+/id-(\d+)/)', h):
            url, pid = m.group(1), m.group(2)
            if pid not in achados:
                achados[pid] = CHAVES + url
                novos += 1
        if not novos or "Página não encontrada" in h[:3000]:
            break
    return achados


def chaves_busca():
    caminhos = []
    for cid in CHAVES_CIDADES:
        caminhos.append(f"/casas-a-venda/{cid}/2-quartos/")
        nome = CHAVES_CIDADES[cid]
        for b in sorted({sem_acento(x).replace(" ", "-") for x in BOA[nome] + ATENCAO[nome]}):
            caminhos.append(f"/casas-a-venda/{cid}/{b}/2-quartos/")
    todos = {}
    with ThreadPoolExecutor(8) as ex:
        for r in ex.map(chaves_links, caminhos):
            todos.update(r)
    return todos


def chaves_detalhe(par):
    pid, url = par
    m = CHAVES_LINK.search(url)
    if not m or int(m.group(3)) > PRECO_MAX or int(m.group(1)) < 2:
        return None
    final, h = baixar(url)
    if not h or f"/id-{pid}/" not in final:
        return None
    titulo = re.search(r"<title>(.*?)</title>", h, re.S)
    titulo = re.sub(r"\s+", " ", html.unescape(titulo.group(1))) if titulo else ""
    # "Casa com 2 quartos na Rua X, Vila Palmares, Santo André - SP - ID: 123 | Chaves na Mão"
    t = re.match(r"Casa com \d+ quartos? (?:na|no|em) (.+?) - SP", titulo)
    if not t:
        return None
    partes = [p.strip() for p in t.group(1).split(",")]
    cidade = partes[-1]
    if cidade not in CIDADES.values() or len(partes) < 2:
        return None
    bairro = partes[-2]
    descs = re.findall(r'"description":"([^"]{40,2500})', h)
    desc = html.unescape(max(descs, key=len)) if descs else ""
    if BLOQUEIO.search(titulo + " " + desc):
        return None
    mod = re.search(r'"dateModified":"(\d{4}-\d{2}-\d{2})', h)
    data = mod.group(1) if mod else None
    if data and (date.today() - date.fromisoformat(data)).days > 365:
        return None
    img = re.search(r'"primaryImageOfPage":\{"@type":"ImageObject","url":"([^"]+)"', h)
    if img and re.search(r"sobrado|condominio", img.group(1)):  # o nome da foto traz a categoria do anúncio
        return None
    gar = re.search(r"(\d+) (?:garagens?|vagas?)", " ".join(descs) + " " + titulo)
    area = int(m.group(2)) if m.group(2) else None
    sb = sem_acento(bairro)
    loc = "atencao" if sb in ATENCAO.get(cidade, []) else "boa" if sb in BOA.get(cidade, []) else "media"
    terrea = bool(re.search(r"t[eé]rrea", desc, re.I))
    return {
        "id": f"chaves-{pid}", "cidade": cidade, "bairro": bairro, "preco": int(m.group(3)),
        "quartos": int(m.group(1)), "vagas": int(gar.group(1)) if gar else None, "area": area,
        "tipo": "Térrea" if terrea else "Casa (confirmar tipo)", "extras": desc[:140],
        "fonte": "Chaves na Mão", "url": final, "link_direto": True, "anuncio_data": data,
        "imagem": img.group(1) if img else None, "localizacao": loc,
        "nota_local": {"boa": "Bairro consolidado e bem servido.", "media": "Bairro residencial; confirme topografia e entorno.", "atencao": "Região periférica ou com ruas em morro."}[loc],
    }


def coletar_chaves(nao):
    links = chaves_busca()
    cand = {p: u for p, u in links.items() if p not in nao and (m := CHAVES_LINK.search(u)) and int(m.group(3)) <= PRECO_MAX and int(m.group(1)) >= 2}
    print("chaves: links", len(links), "candidatos", len(cand))
    with ThreadPoolExecutor(6) as ex:
        return [i for i in ex.map(chaves_detalhe, cand.items()) if i]


def recusadas():
    """Ids numéricos dos anúncios que o Gabriel recusou (decisoes.json)."""
    try:
        d = json.load(open("decisoes.json", encoding="utf-8"))
    except Exception:
        return set()
    return {i.rsplit("-", 1)[-1] for i in d.get("recusadas", [])}


def main():
    todos = {}
    with ThreadPoolExecutor(6) as ex:
        for achados in ex.map(links_da_busca, BUSCAS):
            todos.update(achados)
    print("passada 1:", len(todos))
    with ThreadPoolExecutor(8) as ex:
        for achados in ex.map(links_da_busca, buscas_por_bairro(todos)):
            todos.update(achados)
    print("links de casas térreas:", len(todos))
    nao = recusadas()
    cand = {p: v for p, v in todos.items() if p not in nao and candidato_por_slug(v[1])}
    print("candidatas pelo preço e quartos:", len(cand))
    with ThreadPoolExecutor(6) as ex:
        itens = [i for i in ex.map(detalhe, cand.items()) if i]
    fontes = [a for a in sys.argv[1:] if not a.startswith("--")]
    try:
        itens += coletar_chaves(nao)
    except Exception as e:  # uma fonte fora do ar não derruba as outras
        print("chaves falhou:", e)
    import fontes_extra
    for nome, coletor in fontes_extra.FONTES.items():
        try:
            achados = coletor()
            print(nome + ":", len(achados), "anúncios")
            itens += achados
        except Exception as e:
            print(nome, "falhou:", e)
    itens = [i for i in itens if i["id"].rsplit("-", 1)[-1] not in nao]
    # mesma casa em mais de um portal: mantém uma por bairro, preço e área
    vistos, unicos = set(), []
    for i in sorted(itens, key=lambda x: (x["cidade"], x["bairro"], x["preco"])):
        k = (i["cidade"], i["bairro"], i["preco"], i["area"])
        if k in vistos:
            continue
        vistos.add(k)
        unicos.append(i)
    if len(unicos) < 5:
        sys.exit("poucos resultados, mantendo o arquivo anterior")
    if "--teste" in sys.argv:
        from collections import Counter
        print("TESTE", len(unicos), dict(Counter(i["fonte"] for i in unicos)), dict(Counter(i["cidade"] for i in unicos)))
        return
    import fotos
    try:
        antigas = json.load(open("fotos.json", encoding="utf-8"))
    except (OSError, ValueError):
        antigas = {}
    todas_fotos = fotos.preencher(unicos, antigas)
    saida = {
        "atualizado_em": date.today().isoformat(),
        "fontes_consultadas": sorted({i["fonte"] for i in unicos}),
        "observacao": "Anúncios indisponíveis, com palavras como dívida, financiamento, retomado, sobrado, geminada ou condomínio são removidos automaticamente. Confirme preço e situação com o anunciante.",
        "imoveis": unicos,
        "descartados": [],
    }
    json.dump(saida, open(ARQ, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(todas_fotos, open("fotos.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("gravados:", len(unicos))


if __name__ == "__main__":
    main()
