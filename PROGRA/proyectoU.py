
from flask import Flask, request, session, redirect
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import io, base64, cmath, os

app = Flask(__name__)
app.secret_key = "secret123"

os.makedirs("static", exist_ok=True)


def lagrange(x_vals, y_vals, x):
    total = 0
    for i in range(len(x_vals)):
        term = y_vals[i]
        for j in range(len(x_vals)):
            if i != j:
                term *= (x - x_vals[j]) / (x_vals[i] - x_vals[j])
        total += term
    return total

def newton(x, y, val):
    coef = y.copy()
    for j in range(1, len(x)):
        for i in range(len(x)-1, j-1, -1):
            coef[i] = (coef[i]-coef[i-1])/(x[i]-x[i-j])
    res = coef[-1]
    for i in range(len(x)-2, -1, -1):
        res = res*(val-x[i]) + coef[i]
    return res

def neville(x, y, val):
    n = len(x)
    Q = [[0]*n for _ in range(n)]
    for i in range(n): Q[i][0] = y[i]
    for j in range(1,n):
        for i in range(n-j):
            Q[i][j] = ((val-x[i+j])*Q[i][j-1] + (x[i]-val)*Q[i+1][j-1])/(x[i]-x[i+j])
    return Q[0][n-1]

def muller(f, x0, x1, x2):
    try:
        for _ in range(20):
            h0 = x1-x0; h1 = x2-x1
            d0 = (f(x1)-f(x0))/h0
            d1 = (f(x2)-f(x1))/h1
            a = (d1-d0)/(h1+h0)
            b = a*h1+d1; c = f(x2)
            rad = cmath.sqrt(b*b-4*a*c)
            den = b+rad if abs(b+rad)>abs(b-rad) else b-rad
            if den==0: return None
            x3 = x2-(2*c/den)
            if abs(x3-x2)<1e-6: return x3.real
            x0,x1,x2 = x1,x2,x3
        return None
    except:
        return None



def grafica(x_vals, y_vals, px, py):
    xs, ys = [], []
    x = min(x_vals)-1
    while x <= max(x_vals)+1:
        xs.append(x)
        ys.append(lagrange(x_vals,y_vals,x))
        x+=0.1

    plt.figure(figsize=(5,3.5))
    plt.plot(xs,ys)
    plt.scatter(x_vals,y_vals)
    plt.scatter([px],[py])
    plt.tight_layout()

    img=io.BytesIO()
    plt.savefig(img,format='png',bbox_inches='tight')
    img.seek(0)

    return base64.b64encode(img.getvalue()).decode()

def save_hist(m,r):
    session.setdefault("hist",[])
    session["hist"].append(f"{m}: {round(r,4)}")

def color_modulo(m):
    return {
        "lagrange":"#ff3b30",
        "newton":"#0a84ff",
        "neville":"#30d158",
        "muller":"#bf5af2",
    }.get(m,"#0a84ff")

def welcome():
    return """
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{
margin:0;
height:100vh;
display:flex;
justify-content:center;
align-items:center;
background:linear-gradient(135deg,#0a84ff,#5ac8fa);
overflow:hidden;
font-family:-apple-system;
}

.bubble{
position:absolute;
bottom:-120px;
background:rgba(255,255,255,0.3);
border-radius:50%;
animation:float 8s linear infinite;
}
.b1{width:20px;height:20px;left:10%;}
.b2{width:30px;height:30px;left:30%;}
.b3{width:25px;height:25px;left:60%;}
.b4{width:15px;height:15px;left:80%;}

@keyframes float{
0%{transform:translateY(0);}
100%{transform:translateY(-900px);}
}

.box{text-align:center;color:white;}
.title{font-size:40px;font-weight:700;}

button{
margin-top:30px;
padding:15px 40px;
border:none;
border-radius:20px;
background:white;
color:#0a84ff;
font-size:18px;
font-weight:600;
transition:0.3s;
}
button:hover{transform:scale(1.1);}
</style>
</head>

<body>

<div class="bubble b1"></div>
<div class="bubble b2"></div>
<div class="bubble b3"></div>
<div class="bubble b4"></div>

<div class="box">
<div class="title">MET UMG</div>
<a href="/start"><button>Comenzar</button></a>
</div>

</body>
</html>
"""

def base(title, content, color):
    photo=session.get("photo","")

    return f"""
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>

body{{margin:0;background:#f2f2f7;font-family:-apple-system;overflow:hidden;}}

/* BURBUJAS PRO */
.bubble{{
position:absolute;
bottom:-150px;
background:rgba(90,200,250,0.25);
border-radius:50%;
animation:float 6s linear infinite;
}}

.b1{{width:20px;height:20px;left:5%;}}
.b2{{width:30px;height:30px;left:30%;}}
.b3{{width:25px;height:25px;left:60%;}}
.b4{{width:15px;height:15px;left:80%;}}

@keyframes float{{
0%{{transform:translateY(0) scale(1);}}
50%{{transform:translateY(-400px) scale(1.2);}}
100%{{transform:translateY(-900px) scale(0.8);}}
}}

.header{{display:flex;justify-content:space-between;padding:14px;background:white;animation:slideDown 0.8s;}}

.menu{{display:flex;overflow:auto;background:white;animation:fadeIn 1s;}}
.menu a{{padding:12px;text-decoration:none;color:#555;transition:0.3s;}}
.menu a:hover{{transform:scale(1.15);color:black;}}

.card{{background:white;margin:15px;padding:20px;border-radius:20px;animation:slideUp 0.8s;}}

input{{width:100%;padding:14px;margin-top:10px;border-radius:14px;border:1px solid #ddd;}}
input:focus{{transform:scale(1.05);outline:none;border-color:{color};}}

button{{width:100%;padding:14px;margin-top:12px;border:none;border-radius:14px;background:{color};color:white;}}
button:hover{{transform:scale(1.08);}}

img{{width:100%;margin-top:15px;border-radius:12px;animation:fadeIn 1s;}}

.error{{background:#ff3b30;color:white;padding:10px;border-radius:10px;margin-top:10px;text-align:center;}}

@keyframes slideUp{{from{{opacity:0;transform:translateY(60px);}}to{{opacity:1;}}}}
@keyframes slideDown{{from{{opacity:0;transform:translateY(-60px);}}to{{opacity:1;}}}}
@keyframes fadeIn{{from{{opacity:0;}}to{{opacity:1;}}}}

</style>
</head>

<body>

<div class="bubble b1"></div>
<div class="bubble b2"></div>
<div class="bubble b3"></div>
<div class="bubble b4"></div>

<div class="header">
<div style="font-weight:700;">MET UMG<br><small>{session.get("name","")}</small></div>

<a href="/config">
{"<img src='/"+photo+"' style='width:34px;height:34px;border-radius:50%;'>" if photo else "<div style='width:34px;height:34px;border-radius:50%;background:#ccc;'></div>"}
</a>
</div>

<div class="menu">
<a href="/">Lagrange</a>
<a href="/?m=newton">Newton</a>
<a href="/?m=neville">Neville</a>
<a href="/?m=muller">Müller</a>
<a href="/historial">Historial</a>
</div>

<div class="card">
<h3 style="color:{color};">{title}</h3>
{content}
</div>

</body>
</html>
"""

def render_main(res,img,m,error=""):
    color=color_modulo(m)

    form=f"""
    <form method="post">
    <input name="x_vals" inputmode="decimal" placeholder="x:1,2,3">
    <input name="y_vals" inputmode="decimal" placeholder="y:2,4,6">
    <input name="x" inputmode="decimal" placeholder="valor">
    {"<input name='func' placeholder='función'>" if m=="muller" else ""}
    <button>Calcular</button>
    </form>
    {"<div class='error'>"+error+"</div>" if error else ""}
    <h3>{res}</h3>
    {"<img src='data:image/png;base64,"+img+"'>" if img else ""}
    """

    return base("Interpolation Studio", form, color)

@app.route("/", methods=["GET","POST"])
def home():
    if not session.get("start"):
        return welcome()

    m=request.args.get("m","lagrange")
    res,img,error="","",""

    if request.method=="POST":
        try:
            x=list(map(float,request.form["x_vals"].split(",")))
            y=list(map(float,request.form["y_vals"].split(",")))
            val=float(request.form["x"])

            if len(x)!=len(y):
                raise ValueError

            if m=="lagrange": res=lagrange(x,y,val)
            elif m=="newton": res=newton(x,y,val)
            elif m=="neville": res=neville(x,y,val)
            elif m=="muller":
                f=lambda x:eval(request.form["func"])
                res=muller(f,x[0],x[1],x[2])

            save_hist(m,res)
            img=grafica(x,y,val,res)

        except:
            error="Datos inválidos"

    return render_main(res,img,m,error)

@app.route("/start")
def start():
    session["start"]=True
    return redirect("/")

@app.route("/historial")
def historial():
    items="".join([f"<p>{i}</p>" for i in session.get("hist",[])])
    btn="<a href='/clear'><button style='background:#ff3b30;'>Limpiar historial</button></a>"
    return base("Historial", items+btn, "#5ac8fa")

@app.route("/clear")
def clear():
    session["hist"]=[]
    return redirect("/historial")

@app.route("/config", methods=["GET","POST"])
def config():
    if request.method=="POST":
        session["name"]=request.form.get("name")

        f=request.files.get("photo")
        if f and f.filename!="":
            path="static/"+f.filename
            f.save(path)
            session["photo"]=path

    nombre=session.get("name","")

    form=f"""
    <form method='post' enctype='multipart/form-data'>
    <input name='name' placeholder='Nombre' value='{nombre}'>
    <input type='file' name='photo'>
    <button>Guardar</button>
    </form>

    <a href="/"><button style="background:#ccc;color:black;">Volver</button></a>
    """

    return base("Configuración", form, "#ff9f0a")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
