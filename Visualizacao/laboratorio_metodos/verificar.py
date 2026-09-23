"""Smoke test das nove etapas didáticas e de suas interações."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

HERE=Path(__file__).resolve().parent
OUT=HERE/'qa';OUT.mkdir(exist_ok=True)
errors=[]
with sync_playwright() as p:
 browser=p.chromium.launch()
 page=browser.new_page(viewport={'width':1366,'height':900},device_scale_factor=1)
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto((HERE/'index.html').as_uri())
 for topic,key in [('motor','m'),('granger','g'),('estoque','s')]:
  page.locator(f'[data-tab="{topic}"]').click()
  for step in range(3):
   page.locator(f'[data-{key}step="{step}"]').click()
   assert page.locator(f'#{key}-step-label').inner_text()==f'PASSO {step+1} DE 3'
   assert page.locator(f'#{key}-art').inner_text().strip()
   page.screenshot(path=str(OUT/f'{topic}-{step+1}.png'),full_page=True)
  if topic=='motor':
   page.locator('[data-mequal]').click()
   assert len(set(page.locator('.effect b').all_text_contents()))==1
   page.locator('[data-myear="2023"]').click()
   assert '−' in page.locator('.big-change').inner_text() if page.locator('.big-change').count() else True
  if topic=='granger':
   page.locator('[data-gdir="REVERSO"]').click()
   assert '0,4549' in page.locator('#g-art').inner_text()
   page.locator('[data-gstep="1"]').click()
   page.locator('[data-gyear="2019"]').click()
   assert '2019' in page.locator('#g-art').inner_text()
   assert 'pastagem no Norte' in page.locator('#g-art').inner_text()
  if topic=='estoque':
   page.locator('[data-sregion="Norte"]').click()
   assert 'aumentou' in page.locator('#s-art').inner_text()
   page.locator('[data-sstep="1"]').click()
   for toy in ['half','rate','both']:
    page.locator(f'[data-stoy="{toy}"]').click()
    assert 'ha' in page.locator('#s-art').inner_text()
 for width in [768,390,320]:
  page.set_viewport_size({'width':width,'height':900})
  for topic,key in [('motor','m'),('granger','g'),('estoque','s')]:
   page.locator(f'[data-tab="{topic}"]').click()
   for step in range(3):
    page.locator(f'[data-{key}step="{step}"]').click()
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),(width,topic,step)
    if width==390:page.screenshot(path=str(OUT/f'{topic}-{step+1}-mobile.png'),full_page=True)
 for name,topic in [('motor-comum','motor'),('granger-toda-yamamoto','granger'),('estoque-taxa','estoque')]:
  page.goto((HERE/f'{name}.html').as_uri())
  assert page.locator(f'#{topic}').is_visible()
 assert not errors,errors
 browser.close()
(OUT/'verificacao.json').write_text(json.dumps({'status':'ok','js_errors':errors,'widths':[1366,768,390,320],'steps':9,'standalone_files':3},ensure_ascii=False,indent=2),encoding='utf-8')
print('OK: 9 etapas, interações essenciais, 4 larguras, 3 arquivos independentes e nenhum erro JS.')
