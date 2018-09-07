<img src="logo.png" alt="drawing" width="360"/>

# GetElevation
Plugin Qgis 2 para obtenção de dados de elevação da API Google Maps.

## Instalação
1. Acesse a página de dowloads e baixe a versão mais recente do GetElevation plugin.
2. Extraia os arquivos na pasta de plugins do seu sistema. No Windowns esta pasta localiza-se em C:\Users\Nome do Usuário\.qgis2\python\plugins\
3. Inicie o Qgis.
4. Abra o gerenciador de complementos do Qgis, pelo menu Complementos > Gerenciador de Complementos.
5. Procure pelo plugin Get Elevation e clique no botão "instalar complemento".

## Modos de uso
O Get Elevation apresenta dois modos de entrada de dados
1. Por meio de uma camada vetorial do tipo pontos carregada previamente no projeto do Qgis.
2. Gera uma grade regular de pontos, com base em uma extensão e intervalo de distância entre os pontos.
Como modos de saída o Get Elevation permite salvar na memória ou salvar em arquivo shape.

## Recomendações
A API Google Maps apresenta um limite de consultas, por este motivo, caso seja consultada uma grande quantidade de pontos, o plugin não completará a execução.

## Créditos
Este plugin foi desenvolvido por Rodrigo Sousa.

A melhor forma de referenciar o uso do plugin é: SOUSA, F. R. C. <strong>Get Elevation</strong>. Disponível em: <https://github.com/QgisPlugins/GetElevation/>. Acesso em: 15 mai 2018.
