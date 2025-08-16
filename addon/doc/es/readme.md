### CloudVision

El complemento ofrece una descripción de fotos, por ejemplo, una chica de 23 años con cabello rubio sonriendo,
reconocimiento de texto,
traducción de texto a otro idioma,
lectura de códigos QR
y reconocimiento de fórmulas matemáticas con Mathpix.

### Configuración del complemento
Abrir el menú de NVDA, Preferencias, Configuración de CloudVision.

### Atajos de teclado
* NVDA + CTRL + I - reconocer el objeto de navegación o el archivo seleccionado en el Explorador. Si presiona dos veces rápidamente, el resultado aparecerá en la ventana de visualización virtual.
* el gesto no está asignado - analizar objeto con Mathpix (para fórmulas matemáticas). Para asignar, ver menú de NVDA, Preferencias, gestos de entrada, categoría CloudVision.
* el gesto no está asignado - copiar el último resultado al portapapeles. Para asignar, ver menú de NVDA, Preferencias, gestos de entrada, categoría CloudVision.

Para el navegador, simplemente configúrelo en el elemento deseado, presione la combinación y el complemento lo reconocerá.
Para un archivo, selecciónelo en el Explorador de Windows sin abrirlo, inmediatamente, sin abrir el archivo, presione la combinación.
Solo se admiten JPG, PNG, GIF.
No añadí PDF, ya que el reconocimiento puede durar 40 minutos o más.

La idea y el código para los archivos seleccionados se toman del complemento "Nao (NVDA Advanced OCR)".

### Integración con Mathpix

Para usar Mathpix para el reconocimiento de fórmulas matemáticas y ecuaciones:

1. Obtenga una clave API de [mathpix.com](https://mathpix.com)
2. Introduzca su clave API en el diálogo de configuración de CloudVision
3. Active la opción "Usar Mathpix para el reconocimiento de fórmulas matemáticas"

Puede usar Mathpix de dos maneras:
* Cuando está habilitado en la configuración, Mathpix se utilizará junto con otros servicios de reconocimiento durante el reconocimiento estándar (NVDA+CTRL+I)
* Puede asignar un atajo de teclado al comando "Analizar objeto con Mathpix" en el diálogo de gestos de entrada de NVDA para usar Mathpix directamente