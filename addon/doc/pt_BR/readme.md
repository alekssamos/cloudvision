### CloudVision

O add-on fornece uma descrição de fotos, por exemplo, uma garota de 23 anos com cabelos loiros sorrindo,
reconhecimento de texto,
tradução de texto para outro idioma,
leitura de QR codes
e reconhecimento de fórmulas matemáticas com Mathpix.

### configurações do add-on.
Abra o menu do NVDA, Preferências, Configurações do CloudVision.

### Atalhos do teclado
* NVDA + CTRL + I - reconhece o objeto do navegador ou o arquivo selecionado no Explorer. Se você pressionar duas vezes rapidamente, o resultado aparecerá na janela de visualização virtual.
* o gesto não está atribuído - analisar objeto com Mathpix (para fórmulas matemáticas). Para atribuir, consulte o menu NVDA, Preferências, gestos de entrada, categoria CloudVision.
* o gesto não está atribuído - copie o último resultado para a área de transferência. Para atribuir, consulte o menu NVDA, Preferências, gestos de entrada, categoria CloudVision.

Para o navegador, basta definir o elemento desejado, pressionar a combinação e o complemento o reconhecerá.
Para um arquivo, selecione-o no Windows Explorer sem abri-lo, imediatamente, sem abrir o arquivo, pressione a combinação.
Apenas JPG, PNG, GIF são suportados.
Não adicionei PDF, pois o reconhecimento pode durar 40 minutos ou mais.

A ideia e o código para os arquivos selecionados são retirados do complemento "Nao (NVDA Advanced OCR)".

### Integração com Mathpix

Para usar o Mathpix para reconhecimento de fórmulas matemáticas e equações:

1. Obtenha uma chave API em [mathpix.com](https://mathpix.com)
2. Insira sua chave API na caixa de diálogo de configurações do CloudVision
3. Ative a opção "Usar Mathpix para reconhecimento de fórmulas matemáticas"

Você pode usar o Mathpix de duas maneiras:
* Quando ativado nas configurações, o Mathpix será usado junto com outros serviços de reconhecimento durante o reconhecimento padrão (NVDA+CTRL+I)
* Você pode atribuir um atalho de teclado ao comando "Analisar objeto com Mathpix" na caixa de diálogo de gestos de entrada do NVDA para usar o Mathpix diretamente
