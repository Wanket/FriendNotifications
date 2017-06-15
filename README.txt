Описание конфигурационного файла:
	путь: patch_to_wot\mods\configs\wanket\FriendNotifications.json 
	кодировка: UTF-8 без BOOM
	формат файла:
		{
			"enable": true, // true - Включить мод
			"debug": false, // true - Включить дебаг. Не включайте без необходимости
			"trackingFriends": true, // true - Включить слежение за друзьями
			"trackingClan": false, // true - Включить слежение за соклановцами
			
			"friendConnectedStr": "Игрок {{nameUser}} вошел в игру", // Строка входа друга в игру, поддерживает макросы
			"friendDisconnectedStr": "Игрок {{nameUser}} вышел из игры", // Строка выхода друга в игру, поддерживает макросы
			"clanConnectedStr": "Игрок {{nameUser}} вошел в игру", // Строка входа соклановца в игру, поддерживает макросы
			"clanDisconnectedStr": "Игрок {{nameUser}} вышел из игры" // Строка выхода соклановца в игру, поддерживает макросы
		}
		
		макросы:
		{{nameUser}} - только имя игрока
		{{fullNameUser}} - полное имя игрока, включая клантег
		{{time}} - локальное время в формате Часы:Минуты:Секунды
	