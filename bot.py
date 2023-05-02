from vk_api.longpoll import VkLongPoll, VkEventType
import datetime
import vk_api
from config import user_token, group_token
from random import randrange
from bd import insert_data_seen_person, check, conn


class Bot:
    age_from = 0
    age_to = 0
    looking_persons_offset = 0
    list_found_persons = []

    def __init__(self):
        print('Бот запущен')
        # Создаем переменную сессии, авторизованную личным токеном пользователя.
        self.vk_user = vk_api.VkApi(token=user_token)
        # # переменную сессии vk_user подключаем к api списку методов.
        self.vk_user_got_api = self.vk_user.get_api()
        # Создаем переменную сессии, авторизованную токеном сообщества.
        self.vk_group = vk_api.VkApi(token=group_token)
        # переменную сессии vk_group подключаем к api списку методов.
        self.vk_group_got_api = self.vk_group.get_api()
        # переменную сессии vk_group_got_api подключаем к Long Poll API,
        self.longpoll = VkLongPoll(self.vk_group)
        # позволяет работать с событиями из вашего сообщества в реальном времени.

    def send_msg(self, user_id, message, keyboard):
        """МЕТОД ОТПРАВКИ СООБЩЕНИЙ"""
        self.vk_group_got_api.messages.send(
            user_id=user_id,
            message=message,
            keyboard=keyboard.get_keyboard() if keyboard is not None else None,
            random_id=randrange(10 ** 7)
        )

    def name(self, user_id):
        """ПОЛУЧЕНИЕ ИМЕНИ ПОЛЬЗОВАТЕЛЯ, КОТОРЫЙ НАПИСАЛ БОТУ"""
        user_info = self.vk_group_got_api.users.get(user_id=user_id)
        if user_info:
            name = user_info[0]['first_name']
            return name
        else:
            self.send_msg(
                user_id, "Произошла ошибка, не удалось получить имя пользователя.", keyboard=None)
            return None

    def naming_of_years(self, years, till=True):
        """ДОПОЛНЕНИЕ К ГОДАМ"""
        if till is True:
            name_years = [1, 21, 31, 41, 51, 61, 71, 81, 91, 101]
            if years in name_years:
                return f'{years} года'
            else:
                return f'{years} лет'
        else:
            name_years = [2, 3, 4, 22, 23, 24, 32, 33,
                          34, 42, 43, 44, 52, 53, 54, 62, 63, 64]
            if years == 1 or years == 21 or years == 31 or years == 41 or years == 51 or years == 61:
                return f'{years} год'
            elif years in name_years:
                return f'{years} года'
            else:
                return f'{years} лет'

    def input_looking_age(self, user_id, age):
        a = age.split("-")
        try:
            self.age_from = int(a[0])
            self.age_to = int(a[1])
            if self.age_from == self.age_to:
                self.send_msg(
                    user_id, f' Ищем возраст {self.naming_of_years(self.age_to, False)}', keyboard=None)
                return
            self.send_msg(
                user_id, f' Ищем возраст в пределах от {self.age_from} и до {self.naming_of_years(self.age_to, True)}', keyboard=None)
            return
        except IndexError:
            self.age_to = int(age)
            self.send_msg(
                user_id, f' Ищем возраст {self.naming_of_years(self.age_to, False)}', keyboard=None)
            return
        except ValueError:
            self.send_msg(
                user_id, f' Введен не правильный числовой формат!', keyboard=None)
        return self.get_age_of_user(user_id)

    def get_years_of_person(self, bdate: str) -> object:
        """ОПРЕДЕЛЯЕМ КОЛИЧЕСТВО ЛЕТ"""
        bdate_splited = bdate.split(".")
        month = ""
        try:
            reverse_bdate = datetime.date(int(bdate_splited[2]), int(
                bdate_splited[1]), int(bdate_splited[0]))
            today = datetime.date.today()
            years = (today.year - reverse_bdate.year)
            if reverse_bdate.month >= today.month and reverse_bdate.day > today.day or reverse_bdate.month > today.month:
                years -= 1
            return self.naming_of_years(years, False)
        except IndexError:
            if bdate_splited[1] == "1":
                month = "января"
            elif bdate_splited[1] == "2":
                month = "февраля"
            elif bdate_splited[1] == "3":
                month = "марта"
            elif bdate_splited[1] == "4":
                month = "апреля"
            elif bdate_splited[1] == "5":
                month = "мая"
            elif bdate_splited[1] == "6":
                month = "июня"
            elif bdate_splited[1] == "7":
                month = "июля"
            elif bdate_splited[1] == "8":
                month = "августа"
            elif bdate_splited[1] == "9":
                month = "сентября"
            elif bdate_splited[1] == "10":
                month = "октября"
            elif bdate_splited[1] == "11":
                month = "ноября"
            elif bdate_splited[1] == "12":
                month = "декабря"
            return f'День рождения {int(bdate_splited[0])} {month}.'

    def get_age_of_user(self, user_id):
        """ОПРЕДЕЛЯЕМ ВОЗРАСТ ПОЛЬЗОВАТЕЛЯ"""
        try:
            info = self.vk_user_got_api.users.get(
                user_ids=user_id,
                fields="bdate",
            )[0]['bdate']
            num_age = self.get_years_of_person(info).split()[0]
            self.age_from = num_age
            self.age_to = num_age
            if num_age == "День":
                print(f'Ваш {self.get_years_of_person(info)}')
                self.send_msg(user_id,
                              f' Бот ищет людей вашего возраста, но в ваших настройках профиля установлен пункт "Показывать только месяц и день рождения"! \n'
                              f' Поэтому, введите возраст для поиска, например от 21 года и до 35 лет, в формате : 21-35 (или 21 конкретный возраст 21 год).', keyboard=None)
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        age = event.text
                        return self.input_looking_age(user_id, age)
            return print(f' Ищем вашего возраста {self.naming_of_years(self.age_to)}')
        except KeyError:
            print(f'День рождения скрыт настройками приватности!')
            self.send_msg(user_id,
                          f' Бот ищет людей вашего возраста, но в ваших в настройках профиля установлен пункт "Не показывать дату рождения". '
                          f'\n Поэтому, введите возраст для поиска, например от 21 года и до 35 лет, в формате : 21-35 (или 21 конкретный возраст 21 год).', keyboard=None
                          )
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    age = event.text
                    return self.input_looking_age(user_id, age)

    def get_target_city(self, user_id):
        """ОПРЕДЕЛЯЕТ ГОРОД ДЛЯ ПОЛЬЗОВАТЕЛЯ"""
        global city_id, city_title
        self.send_msg(user_id,
                      f' Введите "Да" - поиск будет произведен в городе указанный в профиле.'
                      f' Или введите название города, например: Москва', keyboard=None
                      )
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                answer = event.text.lower()
                if answer == "да" or answer == "yes":
                    info = self.vk_user_got_api.users.get(
                        user_id=user_id,
                        fields="city"
                    )
                    city_id = info[0]['city']["id"]
                    city_title = info[0]['city']["title"]
                    return f' в городе {city_title}.'
                else:
                    cities = self.vk_user_got_api.database.getCities(
                        country_id=1,
                        q=answer.capitalize(),
                        need_all=1,
                        count=1000
                    )['items']
                    for i in cities:
                        if i["title"] == answer.capitalize():
                            city_id = i["id"]
                            city_title = answer.capitalize()
                            return f' в городе {city_title}'

    def looking_for_gender(self, user_id):
        """ПОЛУЧЕНИЕ ПОЛА ПОЛЬЗОВАТЕЛЯ, МЕНЯЕТ НА ПРОТИВОПОЛОЖНЫЙ"""
        info = self.vk_user_got_api.users.get(
            user_id=user_id,
            fields="sex"
        )
        if info[0]['sex'] == 1:  # 1 — женщина, 2 — мужчина,
            print(f'Ваш пол женский, ищем мужчину.')
            return 2
        elif info[0]['sex'] == 2:
            print(f'Ваш пол мужской, ищем женщину.')
            return 1
        else:
            print("ERROR!!!")

    def looking_for_persons(self, user_id):
        """ ПОИСК АНКЕТЫ НА ОСНОВЕ ПОЛУЧЕННЫХ ДАННЫХ """
        try:
            res = self.vk_user_got_api.users.search(  # group_token недоступен для этого метода users.search.
                sort=0,  # 1 — по дате регистрации, 0 — по популярности.
                city=city_id,
                hometown=city_title,
                # 1— женщина, 2 — мужчина, 0 — любой (по умолчанию).
                sex=self.looking_for_gender(user_id),
                # 1 — не женат или не замужем, 6 — в активном поиске.
                status=1,
                age_from=self.age_from,
                age_to=self.age_to,
                has_photo=1,  # 1 — искать только пользователей с фотографией, 0 — искать по всем пользователям
                count=100,
                offset=self.looking_persons_offset,
                # Информация о том, может ли текущий пользователь отправить личное сообщение. Возможные значения: 1 — может; 0 — не может.
                fields="can_write_private_message, "
                # Информация о городе, указанном на странице пользователя в разделе «Контакты».
                "city, "
                "domain, "  # Короткий адрес страницы.
                "home_town, "  # Название родного города.
            )
        except:
            self.send_msg(
                user_id, f'Повторите попытку, что то пошло не так...')
        number = 0
        for person in res["items"]:
            if not person["is_closed"] and check(conn, user_id, person["id"]):
                if "city" in person and person["city"]["id"] == city_id and person["city"]["title"] == city_title:
                    number += 1
                    id_vk = person["id"]
                    self.list_found_persons.append(id_vk)
        print(
            f'Бот нашел  {number} открытых профилей для просмотра из {len(res["items"])}/{res["count"]} с офсетом {self.looking_persons_offset}')
        return

    def photo_of_found_person(self, user_id):
        """ПОЛУЧЕНИЕ ФОТОГРАФИЙ ПОЛЬЗОВАТЕЛЯ"""
        res = self.vk_user_got_api.photos.get(
            owner_id=user_id,
            # wall — фотографии со стены, profile — фотографии профиля.
            album_id="profile",
            extended=1,  # 1 — будут возвращены дополнительные поля likes, comments, tags, can_comment, reposts. По
            # умолчанию: 0.
            count=30
        )
        dict_photos = dict()
        for i in res['items']:
            photo_id = str(i["id"])
            i_likes = i["likes"]
            # i_comments = i["comments"]
            if i_likes["count"]:
                likes = i_likes["count"]
                dict_photos[likes] = photo_id
        list_of_ids = sorted(dict_photos.items(), reverse=True)
        attachments = []
        photo_ids = []
        for i in list_of_ids:
            photo_ids.append(i[1])
        try:
            attachments.append('photo{}_{}'.format(user_id, photo_ids[0]))
            attachments.append('photo{}_{}'.format(user_id, photo_ids[1]))
            attachments.append('photo{}_{}'.format(user_id, photo_ids[2]))
            return attachments
        except IndexError:
            try:
                attachments.append('photo{}_{}'.format(user_id, photo_ids[0]))
                return attachments
            except IndexError:
                return print(f'Нет фото')

    def get_found_person_id(self):
        return self.list_found_persons.pop()
        # seen_person = []
        # for i in check(conn, ):
        #     seen_person.append(int(i[0]))
        # if not seen_person:
        #     try:
        #         unique_person_id = self.list_found_persons[0]
        #         return unique_person_id
        #     except NameError:
        #         found_persons = 0
        #         return found_persons
        # else:
        #     try:
        #         for ifp in self.list_found_persons:
        #             if ifp in seen_person:
        #                 pass
        #             else:
        #                 unique_person_id = ifp
        #                 return unique_person_id
        #     except NameError:
        #         found_persons = 0
        #         return found_persons

    def found_person_info(self, show_person_id):
        """ИНФОРМАЦИЯ ИЗ АНКЕТЫ НАЙДЕННОЙ """
        res = self.vk_user_got_api.users.get(
            user_ids=show_person_id,
            fields="about, "  # Содержимое поля «О себе» из профиля.
                   "activities, "  # Содержимое поля «Деятельность» из профиля.
                   # Дата рождения. Возвращается в формате D.M.YYYY или D.M (если год рождения скрыт). Если дата рождения скрыта целиком, поле отсутствует в ответе.
                   "bdate, "
                   "status, "
                   # Информация о том, может ли текущий пользователь отправить личное сообщение. Возможные значения: 1 — может; 0 — не может.
                   "can_write_private_message, "
                   # Информация о городе, указанном на странице пользователя в разделе «Контакты».
                   "city, "
                   # Количество общих друзей с текущим пользователем.
                   "common_count, "
                   # Информация о телефонных номерах пользователя. Если данные указаны и не скрыты настройками приватности.
                   "contacts, "
                   "domain, "  # Короткий адрес страницы.
                   "home_town, "  # Название родного города.
                   "interests, "  # Содержимое поля «Интересы» из профиля.
                   # Содержимое поля «Любимые фильмы» из профиля пользователя.
                   "movies, "
                   # Содержимое поля «Любимая музыка» из профиля пользователя.
                   "music, "
                   # Информация о текущем роде занятия пользователя.
                   "occupation"
        )
        first_name = res[0]["first_name"]
        last_name = res[0]["last_name"]
        age = self.get_years_of_person(res[0]["bdate"])
        vk_link = 'vk.com/' + res[0]["domain"]
        city = ''
        try:
            if res[0]["city"]["title"] is not None:
                city = f'Город {res[0]["city"]["title"]}'
            else:
                city = f'Город {res[0]["home_town"]}'
        except KeyError:
            pass
        print(f'{first_name} {last_name}, {age}, {city}. {vk_link}')
        return f'{first_name} {last_name}, {age}, {city}. {vk_link}'

    def send_photo(self, user_id, message, attachments):
        """МЕТОД ОТПРАВКИ СООБЩЕНИЙ С ФОТО"""
        try:
            self.vk_group_got_api.messages.send(
                user_id=user_id,
                message=message,
                random_id=randrange(10 ** 7),
                attachment=",".join(attachments)
            )
        except TypeError:
            pass

    def show_found_person(self, user_id):
        """ПОКАЗЫВАЕТ АНКЕТУ ПОЛЬЗОВАТЕЛЯ"""
        print(self.get_found_person_id())
        if self.get_found_person_id() == None:
            self.send_msg(user_id,
                          f'Все анекты просмотрены. Будет выполнен новый поиск. '
                          f'Измените критерии поиска (возраст, город). '
                          f'Введите возраст для поиска, например от 21 года и до 35 лет, '
                          f'в формате : 21-35 (или 21 конкретный возраст 21 год).  ', keyboard=None)
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    age = event.text
                    self.input_looking_age(user_id, age)
                    self.get_target_city(user_id)
                    self.looking_for_persons(user_id)
                    self.show_found_person(user_id)
                    return
        else:
            ws_id = self.get_found_person_id()
            self.send_msg(user_id, self.found_person_info(
                ws_id), keyboard=None)
            self.send_photo(user_id, 'Фото с максимальными лайками',
                            self.photo_of_found_person(ws_id))
            insert_data_seen_person(conn, user_id, ws_id)


bot = Bot()
