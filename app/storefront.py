"""HTML and product data for the ShopNow storefront."""

PRODUCTS = [
    {"id": 1, "nome": "Celular", "preco": 8586.90, "icone": "📱"},
    {"id": 2, "nome": "Ração", "preco": 650.00, "icone": "🐶"},
    {"id": 3, "nome": "Fralda", "preco": 300.00, "icone": "👶"},
    {"id": 4, "nome": "TV", "preco": 9999.99, "icone": "📺"},
    {"id": 5, "nome": "Sofa", "preco": 3000.00, "icone": "🛋️"},
]

CORES = {"app1": "#2563eb", "app2": "#16a34a", "app3": "#ea580c"}


def preco_br(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def render_home(server_name: str) -> str:
    cor = CORES.get(server_name, "#2563eb")
    cards = "".join(
        f"""<article class="card">
              <div class="icone">{p['icone']}</div>
              <span class="desconto">30% OFF</span>
              <h2>{p['nome']}</h2>
              <p class="preco-antigo">{preco_br(p['preco'] / 0.7)}</p>
              <p class="preco">{preco_br(p['preco'])}</p>
              <button onclick="comprar(this)">Comprar</button>
            </article>"""
        for p in PRODUCTS
    )
    return f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ShopNow - Ofertas</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: #f4f6f8; color: #222; font-family: Arial, sans-serif; }}
  header {{ padding: 18px 8%; background: #fff; display: flex; justify-content: space-between; align-items: center; }}
  .logo {{ color: #222; font-size: 24px; font-weight: bold; text-decoration: none; }}
  .logo span {{ color: #2563eb; }}
  .server {{ color: {cor}; font-size: 13px; }}
  .banner {{ padding: 36px 20px; background: #dceaff; text-align: center; }}
  .banner h1 {{ margin: 0 0 10px; color: #173c70; font-size: 34px; }}
  .banner p {{ margin: 0; color: #40546e; }}
  .container {{ max-width: 1100px; margin: 30px auto; padding: 0 20px; }}
  .container h2 {{ margin-bottom: 20px; font-size: 24px; }}
  main {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 18px; }}
  .card {{ position: relative; padding: 18px; background: #fff; border: 1px solid #e1e5e9; border-radius: 6px; }}
  .icone {{ height: 110px; display: grid; place-items: center; background: #f4f6f8; font-size: 58px; }}
  .desconto {{ position: absolute; top: 26px; left: 26px; padding: 5px 8px; background: #e74c3c; color: #fff; font-size: 11px; }}
  .card h2 {{ margin: 15px 0 8px; font-size: 18px; }}
  .preco-antigo {{ margin: 0; color: #888; font-size: 13px; text-decoration: line-through; }}
  .preco {{ margin: 4px 0 14px; color: #16803c; font-size: 20px; font-weight: bold; }}
  button {{ width: 100%; padding: 10px; border: 0; border-radius: 4px; background: #2563eb; color: #fff; font-size: 14px; cursor: pointer; }}
  button:hover {{ background: #174bbd; }}
  button:disabled {{ opacity: .6; cursor: wait; }}
  footer {{ padding: 18px; color: #777; font-size: 13px; text-align: center; }}
  footer b {{ color: {cor}; }}
  #toast {{ position: fixed; right: 20px; bottom: 20px; display: none; padding: 14px 18px; background: #222; color: #fff; border-radius: 4px; }}
  @media (max-width: 500px) {{
    header {{ padding: 16px 5%; }}
    .banner h1 {{ font-size: 28px; }}
    .container {{ margin-top: 22px; }}
    main {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }}
    .card {{ padding: 12px; }}
    .icone {{ height: 90px; }}
    .desconto {{ top: 19px; left: 19px; }}
  }}
</style>
</head>
<body>
  <header>
    <a class="logo" href="/">Shop<span>Now</span></a>
    <span class="server">Servidor: {server_name.upper()}</span>
  </header>
  <section class="banner">
    <h1>Ofertas da semana</h1>
    <p>Aproveite 30% de desconto em produtos selecionados</p>
  </section>
  <section class="container" id="ofertas">
    <h2>Produtos em destaque</h2>
    <main>{cards}</main>
  </section>
  <footer>ShopNow · Página atendida pela instância <b>{server_name}</b></footer>
  <div id="toast"></div>
<script>
  async function comprar(btn) {{
    btn.disabled = true;
    btn.textContent = "Processando...";
    const toast = document.getElementById("toast");
    try {{
      const response = await fetch("/api/checkout");
      if (!response.ok) throw new Error("Falha ao processar o pedido");
      const result = await response.json();
      toast.textContent = "Pedido confirmado pelo servidor " + result.server;
    }} catch (error) {{
      toast.textContent = "Não foi possível concluir o pedido.";
    }} finally {{
      btn.disabled = false;
      btn.textContent = "Comprar";
    }}
    toast.style.display = "block";
    setTimeout(() => toast.style.display = "none", 3000);
  }}
</script>
</body>
</html>"""
