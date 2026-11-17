# CineBoard

Контрольная работа по Django: каталог фильмов на CBV.

- регистрация и вход (стандартные формы Django)
- CRUD фильмов, ListView и DetailView, поиск по названию
- фильтр по жанру (ManyToMany), комментарии (ForeignKey, только для авторизованных), VIP-бронь (OneToOne с User)

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata movies
python manage.py runserver
```
