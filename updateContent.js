// Функция для обновления содержимого файла
function updateContent() {
    // Создаем новый объект XMLHttpRequest
    var xhr = new XMLHttpRequest();

    // Открываем новый GET-запрос к файлу
    xhr.open("GET", "index.html", true);

    // Устанавливаем обработчик события onload для обработки ответа сервера
    xhr.onload = function () {
        if (xhr.status == 200) {
            // Если запрос успешно выполнен, обновляем содержимое элемента на странице
            document.documentElement.innerHTML = xhr.responseText;
        }
    };

    // Отправляем запрос
    xhr.send();
}

// Устанавливаем интервал для обновления содержимого файла каждую минуту
setInterval(updateContent, 60000);