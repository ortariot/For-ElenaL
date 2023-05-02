from vk_api.longpoll import VkEventType, VkLongPoll
from bot import *
from bd import *
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from config import *
keyboard = VkKeyboard(one_time=True)

for event in bot.longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        user_id = event.user_id
        if request == 'start' or request == 'привет':
            keyboard = VkKeyboard(one_time=True)
            buttons = ['поиск', 'смотреть', 'удалить']
            button_colors = [VkKeyboardColor.NEGATIVE,
                             VkKeyboardColor.PRIMARY, VkKeyboardColor.POSITIVE]
            for btn, btn_color in zip(buttons, button_colors):
                keyboard.add_button(btn, btn_color)
            bot.send_msg(user_id, f'{bot.name(user_id)} Бот готов к поиску, нажмите кнопку: \n '
                                  f' "Поиск" - Поиск людей. \n'
                                  f' "Удалить" - удаляет старую БД и создает новую. \n'
                                  f' "Смотреть" - просмотр следующей анкеты.', keyboard)
        elif request == 'поиск':
            bot.get_age_of_user(user_id)
            bot.get_target_city(user_id)
            # выводит список в чат найденных людей и добавляет их в базу данных.
            bot.looking_for_persons(user_id)
            # выводит в чат инфо одного человека из базы данных.
            bot.show_found_person(user_id)
            bot.send_msg(user_id, f'{bot.name(user_id)} Бот готов продолжить, нажмите кнопку: \n '
                                  f' "Поиск" - Поиск людей с другими параметрами. \n'
                                  f' "Удалить" - удаляет старую БД и создает новую. \n'
                                  f' "Смотреть" - просмотр следующей записи в БД.', keyboard)
        elif request == 'смотреть':
            if bot.get_found_person_id() == None:
                bot.looking_persons_offset += 100
                bot.looking_for_persons(user_id)
            bot.show_found_person(user_id)
            bot.send_msg(
                user_id, f'{bot.name(user_id)} продолжим поиск по заданным параметрам)', keyboard)
            # bot.send_msg(user_id, f'{bot.name(user_id)} Необходимо нажать "поиск" или "удалить"', keyboard)
        elif request == 'удалить':
            delete_table_seen_person()  # удаляет существующую БД.
            create_table_seen_person()  # создает новую БД.
            bot.send_msg(
                user_id, f' База данных очищена! Сейчас нажмите "Поиск"', keyboard)
        else:
            bot.send_msg(user_id, f'{bot.name(user_id)} Бот готов к поиску, нажмите кнопку: \n '
                         f' "Поиск" - Поиск людей. \n'
                         f' "Удалить" - удаляет старую БД и создает новую. \n'
                         f' "Смотреть" - просмотр следующей записи в БД.', keyboard)
