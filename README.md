# Лабораторная работа - Разработка REST API и работа с OpenAPI
pip install fastapi uvicorn[standard] pydantic

Создание файла main.py

uvicorn main:app --reload

<img width="1898" height="964" alt="image" src="https://github.com/user-attachments/assets/9893b724-39c1-4a59-a831-65b12a058197" />

<img width="1903" height="963" alt="image" src="https://github.com/user-attachments/assets/279acb42-ce4b-4a71-bcf8-beb9076091a6" />

Чтение (Read) всей коллекции
GET /api/books
<img width="1798" height="907" alt="image" src="https://github.com/user-attachments/assets/9b7ef5a4-fd3b-4822-9bf2-3b5404f691eb" />

Создание (Create) нового ресурса
POST /api/books
Успешное создание (Проверка кода 201)
<img width="1778" height="824" alt="image" src="https://github.com/user-attachments/assets/e990d6e4-d5e9-49f9-8db7-66f0c2ba86fe" />

Проверка валидации (Проверка кода 422)
<img width="1779" height="911" alt="image" src="https://github.com/user-attachments/assets/feb285db-4653-4451-95da-13dc34b758a6" />

Обновление (Update) ресурса по ID (PUT и PATCH)
Полное обновление (PUT /api/books/{book_id})
<img width="1783" height="825" alt="image" src="https://github.com/user-attachments/assets/146edd60-d4bc-4fe1-94a4-0e2784935da0" />


Частичное обновление (PATCH /api/books/{book_id})
<img width="1773" height="773" alt="image" src="https://github.com/user-attachments/assets/8468035b-53b0-4d37-8616-f5831513c43d" />

Удаление (Delete) ресурса (DELETE /api/books/{book_id})
<img width="1769" height="808" alt="image" src="https://github.com/user-attachments/assets/4d096b6b-54f1-4afd-85b2-443a6367b38b" />


Изучение OpenAPI спецификации (Задание 2.8)
<img width="1749" height="964" alt="image" src="https://github.com/user-attachments/assets/43d61e13-fda5-440c-b424-6a2c48b1c6b0" />

Расширение API (Задание 2.9)






