$(document).ready(function() {
    $('#imagenInput').change(function() {
        var archivo = $(this)[0].files[0];

        if (archivo) {
            var reader = new FileReader();
            reader.onload = function(event) {
                var img = new Image();
                img.onload = function() {
                    var canvas = document.createElement('canvas');
                    var ctx = canvas.getContext('2d');
                    var MAX_WIDTH = 800; // Tamaño máximo deseado para la imagen
                    var MAX_HEIGHT = 600;

                    var width = img.width;
                    var height = img.height;

                    if (width > height) {
                        if (width > MAX_WIDTH) {
                            height *= MAX_WIDTH / width;
                            width = MAX_WIDTH;
                        }
                    } else {
                        if (height > MAX_HEIGHT) {
                            width *= MAX_HEIGHT / height;
                            height = MAX_HEIGHT;
                        }
                    }

                    canvas.width = width;
                    canvas.height = height;
                    ctx.drawImage(img, 0, 0, width, height);

                    var resizedImageDataUrl = canvas.toDataURL('image/jpeg', 0.7); // Comprime la imagen al 70% de calidad
                    var resizedBlob = dataURItoBlob(resizedImageDataUrl);

                    var formData = new FormData();
                    formData.append('imagen', resizedBlob, 'imagen.jpg');

                    var csrftoken = getCookie('csrftoken');

                    $.ajax({
                        url: '/gymapp/lector/',
                        type: 'POST',
                        data: formData,
                        processData: false,
                        contentType: false,
                        headers: {
                            'X-CSRFToken': csrftoken
                        },
                        success: function(response) {
                            console.log('Respuesta del servidor:', response);

                            // Verificar si la operación fue exitosa
                            if (response.success) {
                                console.log('Imagen enviada al backend con éxito');
                                $('#mensaje').text(response.mensaje);

                                // Verificar si hay una URL de redirección en la respuesta
                                if (response.redireccionar) {
                                    // Redirigir al usuario a la URL proporcionada por el servidor
                                    window.location.href = response.redireccionar;
                                }
                            } else {
                                console.error('Error al enviar la imagen al backend: ', response.mensaje);
                            }
                        },
                        error: function(error) {
                            console.error('Error al enviar la imagen al backend: ', error);
                        }
                    });
                };
                img.src = event.target.result;
            };
            reader.readAsDataURL(archivo);
        } else {
            console.error('No se seleccionó ningún archivo.');
        }
    });

    // Funciones dataURItoBlob y getCookie aquí...
});