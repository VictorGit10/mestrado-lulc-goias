# Pasto Legal — Viagem de Campo

Experiência interativa da expedição Pasto Legal pelo Norte de Minas Gerais (24–27 de maio de 2026).

## Arquitetura

```
CampoPastoLegal/
├── index.html              # Estrutura principal
├── css/
│   └── campo.css           # Estilos editoriais, glassmorphism, animações
├── js/
│   ├── dados.js            # Dados estáticos (fazendas, itinerário, equipe)
│   ├── mapa.js             # Leaflet + rota real OSRM + carro animado
│   ├── jornada.js          # Navegação por dias, timeline, overlay
│   └── formulario.js       # Modal e persistência de dados
├── assets/
│   └── rota_completa.json  # Geometria GeoJSON da rota real (OSRM)
└── README.md
```

## Como usar

1. Suba um servidor local:
   ```bash
   python -m http.server 8080
   ```
2. Acesse `http://localhost:8080/CampoPastoLegal/`

## Recursos

- **Hero introdutório** com transição suave para o app
- **Mapa CartoDB Voyager** — estilo elegante tipo Google Maps, não satélite
- **Rota real** calculada via OSRM (Open Source Routing Machine) — não é linha reta
- **Carro animado** que percorre a rota conforme você navega pelos dias
- **Timeline lateral** com cards de jornada para cada dia
- **Overlay flutuante** mostrando o dia e estatísticas ativas
- **Controles** de navegação (anterior, reproduzir, próximo)
- **Formulário de campo** com fallback local + integração Google Sheets

## Configurar Google Sheets

1. Crie uma planilha com colunas: `timestamp`, `fazenda`, `tipo`, `descricao`, `url`, `imagem_base64`
2. Em **Extensões → Apps Script**, implante como **Aplicativo da Web** (acesso "Qualquer pessoa")
3. No console do navegador, execute:
   ```javascript
   localStorage.setItem('pl_sheets_url', 'https://script.google.com/macros/s/SEU_CODIGO/exec');
   ```
4. Recarregue a página

## Ajustes futuros

- **Coordenadas das fazendas:** os pins atuais são centróides municipais. Substitua `FAZENDAS[].coords` em `js/dados.js` pelas lat/lon reais.
- **Cores:** edite as variáveis CSS em `:root` para ajustar a paleta.
