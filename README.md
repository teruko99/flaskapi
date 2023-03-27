# Flask API

A ideia é rodar 3 containers no Docker, um para MongoDB onde serão salvos os usuários, outro com Elasticsearch para manter os logs e por fim o de API que cruza os dados da api da ViaCEP (https://viacep.com.br/), pega a cidade retornada e busca a previsão do tempo dos 4 dias dessa cidade na api do INPE (http://servicos.cptec.inpe.br/XML/).
