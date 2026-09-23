"""Exporta somente leituras; não altera os dados científicos ou os slides."""
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P = ROOT / 'data/processed'

def records(df):
    return json.loads(df.to_json(orient='records', force_ascii=False))

drv = pd.read_csv(P/'drivers_macro_anual.csv').sort_values('ano')
delta = drv.cambio_real_efetivo.diff()
z = (delta-delta.mean())/delta.std(ddof=0)
motor_years = []
for i in range(2, len(drv)):
    motor_years.append(dict(year=int(drv.ano.iloc[i]), shockYear=int(drv.ano.iloc[i-1]),
        before=float(drv.cambio_real_efetivo.iloc[i-2]), after=float(drv.cambio_real_efetivo.iloc[i-1]),
        delta=float(delta.iloc[i-1]), z=float(z.iloc[i-1])))
apt = pd.read_csv(P/'aptidao_edafo_amc.csv')[['code_amc','exp_apt_edafo','lat']]
meta = pd.read_csv(P/'fronteira_estoque_convertivel.csv')[['code_amc','regiao']].drop_duplicates()
apt = apt.merge(meta, on='code_amc').sort_values('exp_apt_edafo')
horse = pd.read_csv(P/'drive_horse_race_latitude.csv')
did = json.loads((ROOT/'Visualizacao/assets/data/didatica_apresentacao.json').read_text(encoding='utf-8'))
series = pd.read_csv(P/'deslocamento_series_regionais.csv').sort_values('ano')
published = pd.read_csv(P/'granger_reverso_estacionaria.csv')
ty = []
for direction in ['Sul→Norte', 'REVERSO']:
    xcol,ycol = ('agric_mha_Sul','pasto_mha_Norte') if direction=='Sul→Norte' else ('pasto_mha_Norte','agric_mha_Sul')
    for p in [1,2]:
        d = pd.DataFrame(dict(year=series.ano, y=series[ycol], x=series[xcol]))
        cols=[]
        for lag in range(1,p+3):
            for v in ['y','x']:
                c=f'{v}{lag}'; d[c]=d[v].shift(lag); cols.append(c)
        d=d.dropna(); X=sm.add_constant(d[cols]); fit=sm.OLS(d.y,X).fit(cov_type='HAC',cov_kwds={'maxlags':2})
        tested=[f'x{k}' for k in range(1,p+1)]
        R=np.array([[float(c==t) for c in X.columns] for t in tested])
        pv=float(np.asarray(fit.f_test(R).pvalue).item())
        official=published[(published.bloco=='toda_yamamoto') & (published.relacao==direction) & (published.p==p)].iloc[0]
        assert abs(pv-official.ty_p)<.000051, (pv, official.ty_p)
        rest=sm.OLS(d.y,X.drop(columns=tested)).fit()
        ty.append(dict(direction=direction,p=p,dmax=2,n=len(d),pvalue=pv,
            years=d.year.astype(int).tolist(), observed=d.y.tolist(),full=fit.fittedvalues.tolist(),
            restricted=rest.fittedvalues.tolist(),ssrFull=float(fit.ssr),ssrRestricted=float(rest.ssr),
            coefficients={k:float(v) for k,v in fit.params.items()}))

stock = pd.read_csv(P/'fronteira_estoque_convertivel.csv')
decomp=pd.read_csv(P/'fronteira_decomposicao.csv')
stocks=[]
for region in ['Sul','Centro','Norte','Goiás (total)']:
    sub=stock if region=='Goiás (total)' else stock[stock.regiao==region]
    acts=[]
    for label,start,end in [('II',2001,2019),('III',2020,2024)]:
        a=sub[sub.ano.between(start,end)]
        S=float(a.groupby('ano').estoque_prev.sum().mean()/1e6)
        F=float(a.groupby('ano').fluxo_ha.sum().mean()/1e6)
        acts.append(dict(label=label,start=start,end=end,stock=S,rate=F/S,flow=F))
    a,b=acts; es=(b['stock']-a['stock'])*(a['rate']+b['rate'])/2
    er=(b['rate']-a['rate'])*(a['stock']+b['stock'])/2
    assert abs(es+er-(b['flow']-a['flow']))<1e-12
    official=decomp[decomp.regiao==region].iloc[0]
    assert abs(es-official.efeito_estoque)<.000051
    stocks.append(dict(region=region,acts=acts,stockEffect=es,rateEffect=er))
data=dict(motor=dict(years=motor_years,amcs=records(apt),models=records(horse[horse.spec.isin(['S1','S4'])]),
    correlation=float(apt.exp_apt_edafo.corr(apt.lat))),granger=did['empurrao']['granger'],ty=ty,stocks=stocks,
    built='2026-09-23', sources=['drivers_macro_anual.csv','aptidao_edafo_amc.csv','drive_horse_race_latitude.csv',
    'deslocamento_series_regionais.csv','granger_reverso_estacionaria.csv','fronteira_estoque_convertivel.csv','fronteira_decomposicao.csv'])
blob=json.dumps(data,ensure_ascii=False,allow_nan=False,separators=(',',':'))
(HERE/'dados.js').write_text('window.LAB_DATA='+blob+';\n',encoding='utf-8')
template=(HERE/'modelo.html').read_text(encoding='utf-8')
html=template.replace('/* CSS_EMBUTIDO */',(HERE/'estilo.css').read_text(encoding='utf-8')).replace('/* DADOS_EMBUTIDOS */','window.LAB_DATA='+blob+';').replace('/* JS_EMBUTIDO */',(HERE/'laboratorio.js').read_text(encoding='utf-8'))
(HERE/'index.html').write_text(html,encoding='utf-8')
for name,scene in [('motor-comum','motor'),('granger-toda-yamamoto','granger'),('estoque-taxa','estoque')]:
    (HERE/f'{name}.html').write_text(html.replace('data-start="motor"',f'data-start="{scene}"'),encoding='utf-8')
print(f'OK: {len(apt)} AMCs; {len(motor_years)} choques defasados; 4 testes TY reproduzidos; 4 decomposições conferidas; HTML {len(html.encode())//1024} KB.')
