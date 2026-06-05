// Dados estáticos da viagem de campo Pasto Legal — Norte de Minas, maio 2026
// Coordenadas das fazendas são centróides municipais com offset para não sobrepor.

const EQUIPE = [
  { nome: "Victor Amaral", papel: "Pesquisador / Dissertação" },
  { nome: "Prof. Laerte", papel: "Orientador" },
  { nome: "Pedro Novaes", papel: "Pesquisador" },
  { nome: "Tiago", papel: "Pesquisador" }
];

const FAZENDAS = [
  {
    id: "caraibas",
    nome: "Faz. Caraíbas",
    codigo_car: "MG-3135100-2B45.1F5D.3D4B.4B76.8D21.A477.F97C.25F2",
    municipio: "Janaúba",
    cod_ibge: "3135100",
    coords: [-15.800, -43.295],
    cor: "#2d6a42",
    dados_coletados: []
  },
  {
    id: "tabajara",
    nome: "Faz. Tabajara",
    codigo_car: "MG-3135100-DC43.57E8.CC3B.4FF0.A8E8.E360.5FF7.F4D7",
    municipio: "Janaúba",
    cod_ibge: "3135100",
    coords: [-15.820, -43.315],
    cor: "#c5922a",
    dados_coletados: []
  },
  {
    id: "santa_angela",
    nome: "Faz. Santa Ângela",
    codigo_car: "MG-3112703-C5ACCE19FF494A4289FC417E05559451",
    municipio: "Capitão Enéas",
    cod_ibge: "3112703",
    coords: [-16.3236018, -43.7154584],
    cor: "#b85c38",
    dados_coletados: []
  },
  {
    id: "tailandia",
    nome: "Faz. Tailândia",
    codigo_car: "MG-3135100-77AE.0769.59E4.0457.4DE7.3C24.8548.56B5",
    municipio: "Janaúba",
    cod_ibge: "3135100",
    coords: [-15.795, -43.280],
    cor: "#4a7ba6",
    dados_coletados: []
  }
];

const ROTA_COORDS = [
  [-16.6869, -49.2648],
  [-16.7495727, -43.8687268],
  [-15.8103735, -43.3052119],
  [-17.3493765, -44.9507904],
  [-16.6869, -49.2648]
];

const ROTA_MUNICIPIOS = [
  { nome: "Goiânia", coords: [-16.6869, -49.2648], tipo: "partida" },
  { nome: "Montes Claros", coords: [-16.7495727, -43.8687268], tipo: "pernoite" },
  { nome: "Janaúba", coords: [-15.8103735, -43.3052119], tipo: "pernoite" },
  { nome: "Pirapora", coords: [-17.3493765, -44.9507904], tipo: "pernoite" },
  { nome: "Goiânia", coords: [-16.6869, -49.2648], tipo: "chegada" }
];

const ITINERARIO = [
  {
    dia: "Domingo, 24/5",
    resumo: "Deslocamento Goiânia → Montes Claros",
    stats: [
      { valor: "850", label: "km" },
      { valor: "~11h", label: "viagem" }
    ],
    atividades: [
      { hora: "06:00", local: "Goiânia", descricao: "Saída em carro da equipe." },
      { hora: "~18:00", local: "Montes Claros", descricao: "Chegada após ~850 km pela BR-040/BR-251. Pernoite em Montes Claros." }
    ],
    fazendas: []
  },
  {
    dia: "Segunda, 25/5",
    resumo: "Montes Claros → Janaúba",
    stats: [
      { valor: "3", label: "fazendas" },
      { valor: "1", label: "reunião" }
    ],
    atividades: [
      { hora: "Manhã", local: "Região de Montes Claros", descricao: "Visita a duas fazendas pequenas na região de Montes Claros." },
      { hora: "15:00", local: "Sindicato Rural / Senar", descricao: "Reunião no Sindicato Rural com Senar." },
      { hora: "Tarde", local: "Entre MOC e Janaúba", descricao: "Visita a fazenda pequena tecnificada entre Montes Claros e Janaúba." },
      { hora: "Noite", local: "Janaúba", descricao: "Pernoite em Janaúba." }
    ],
    fazendas: ["santa_angela"]
  },
  {
    dia: "Terça, 26/5",
    resumo: "Janaúba → Pirapora",
    stats: [
      { valor: "3", label: "fazendas" },
      { valor: "1", label: "pernoite" }
    ],
    atividades: [
      { hora: "Manhã", local: "Fazendas da região de Janaúba", descricao: "Visita a fazendas e acompanhamento de planejamento forrageiro." },
      { hora: "Tarde", local: "Fazendas", descricao: "Continuação de visitas técnicas na região." },
      { hora: "Noite", local: "Pirapora", descricao: "Deslocamento até Pirapora e pernoite." }
    ],
    fazendas: ["caraibas", "tabajara", "tailandia"]
  },
  {
    dia: "Quarta, 27/5",
    resumo: "Retorno Pirapora → Goiânia",
    stats: [
      { valor: "684", label: "km" },
      { valor: "~9h", label: "viagem" }
    ],
    atividades: [
      { hora: "Manhã", local: "Pirapora", descricao: "Saída de Pirapora." },
      { hora: "~18:00", local: "Goiânia", descricao: "Chegada em Goiânia após ~684 km." }
    ],
    fazendas: []
  }
];
