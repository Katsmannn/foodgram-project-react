# FOODGRAM (Кулинарный помощник)
Сервис для обмена кулинарными рецептами  

## Описание проекта
Сервис предоставляет функционал:  
> Регистрация пользователя
> Авторизация зарегистрированного пользователя
> Создание/редактирование/удаление рецепта авторизованным пользователем
> Просмотр рецептов, доступен для неавторизованных пользователей
> Подписка на пользователя/просмотр подписок пользователя
> Добавление рецепта в список избранных/просмотр избранных рецептов
> Добавление рецепта в список покупок
> Просмотр корзины покупок/загрузка списка покупок в виде файла .txt

## Проект доступен по адресу:  
http://51.250.24.142/  
http://konenkovsa.tk/  

## Развёртывание проекта
> Склонировать проект из репозитория  
> Запустить сборку контейнеров проекта  
'''
sudo docker-compose up --build -d
'''
> Выполнить миграции  
'''
sudo docker-compose exec web pyhton manage.py makemigrations
sudo docker-compose exec web pyhton manage.py migrate
'''
> Наполнить базу данными tags, ingredients  
'''
sudo docker-compose exec web pyhton manage.py tags
sudo docker-compose exec web pyhton manage.py ingredients
'''
> Создать суперюзера  
'''
sudo docker-compose exec web pyhton manage.py createsuperuser
'''
> Собрать статику проекта  
'''
sudo docker-compose exec web pyhton manage.py collectstatic
'''

![Status](https://github.com/katsmannn/foodgram-project-react/actions/workflows/foodgram.yml/badge.svg)  
  
### Автор
(c) Коненков Сергей при поддержке Яндекс.Практикум
