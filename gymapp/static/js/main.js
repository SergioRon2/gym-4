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
                            console.log('Imagen enviada al backend con éxito');
                            $('#mensaje').text(response.mensaje);

                            if (response.success) {
                                console.log('si leo el success');
                                var enlace = document.getElementById("miEnlace");

                                // Agrega el ID del código QR a la URL
                                var nuevaURL = enlace.href + '?codigo=' + response.codigo + '&nombre=' + response.name;

                                // Actualiza el atributo href del enlace
                                enlace.href = nuevaURL;

                                // Haz clic en el enlace automáticamente
                                enlace.click();
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

    function dataURItoBlob(dataURI) {
        var byteString = atob(dataURI.split(',')[1]);
        var ab = new ArrayBuffer(byteString.length);
        var ia = new Uint8Array(ab);
        for (var i = 0; i < byteString.length; i++) {
            ia[i] = byteString.charCodeAt(i);
        }
        return new Blob([ab], { type: 'image/jpeg' }); // Cambiado a 'image/jpeg'
    }

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});


// 
// Obtener todos los botones "Pagar"