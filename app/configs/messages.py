from app import filters


START_MESSAGE = 'Привет!\n' \
                'Устал искать свое уютное гнездышко? Доверься мне!\n' \
                'Я могу подобрать случайную квартиру по твоим основным критериям ' \
                'из базы недвижимости ЦИАН (https://cian.ru/).'

SETTINGS_FROM_START = "Как минимум, выберите город и тип предложения."

SEARCH_TERMS = "Настройка критериев поиска."
SEARCH_TERMS_ANSWER = "*Текущие условия:*\n" \
                      "*Город:* {}\n" \
                      "*Тип предложения:* {}\n" \
                      "*Метро:* {}\n"\
                      "*Комнаты:* {}\n" \
                      "*Тип недвижимости:* {}\n" \
                      "*Цены:* {}\n"

GET_CITY = "Укажите город."
GET_DEAL_TYPE = "Ищем, чтобы снять или купить?"
GET_UNDERGROUND1 = "Выберите интересующую ветку метро."
GET_UNDERGROUND2 = "Выберите ближайшую станцию метро."
GET_ROOMS = "Выберите количество комнат. Можно выбрать несколько вариантов.\n" \
            "Чтобы убрать один из вариантов, нажмите на него еще раз."
GET_APARTMENT_TYPE = "Выберите тип жилья."
GET_PRICE = "Задайте интервал цен.\n" \
            "Можете выбрать один из доступных вариантов или задать интервал вручную, отправив сообщение.\n" \
            "Пример сообщения: 0-30000"

CITY_ANSWER = "Установлен город: {}."
DEAL_TYPE_ANSWER = "Установлен тип предложения: {}."
ROOMS_ANSWER = "Установлено количество комнат: {}."
ROOMS_ANSWER_NOT = "Количество комнат не установлено."
APARTMENT_TYPE_ANSWER = "Установлен тип недвижимости: {}."
PRICE_ANSWER = "Установлены цены: {} руб - {} руб."
UNDEGROUND_ANSWER = "Станция метро установлена."

RANDOM_FLAT_WAITING  = "Подбираю..."
RANDOM_FLAT_ANSWER = "*Цена:* {price} руб.\n\n" \
                     "*Метро:* {metro}.\n\n" \
                     "*Адрес:* {street} {house}.\n\n" \
                     "*Общее:* {object_type}, {area}, {floor}.\n\n" \
                     "*Подробнее:* {url}"
RANDOM_FLAT_ERROR = "Не удалось подобрать квартиру. Попробуйте еще раз."
RANDOM_FLAT_EMPTY = "Не удалось найти новую квартиру по вашим критериям."
APART_TYPE_ALERT = "Опция доступна, если выбрали тип предложения 'Купить'."
GET_PRICE_FROM_MSG_ALERT = "Не смог распознать цены, попробуйте еще раз в соответствии с примером."
UNKNOWN_ALERT = "Что-то пошло не так..."


NOTIFICATIONS_MAIN = "Выберите режим уведомлений и получайте квартиры каждый день!\n" \
                     "Бот будет присылать вам сообщения в соответствии с выбранным условием (время МСК):"
NOTIFICATIONS_ANSWER = "Уведомления настроены."
NO_NOTIFICATIONS_ANSWER = "Уведомления отключены."


def search_terms_answer(region, deal, underground, rooms, apartment_type, price):
    city = filters.city_filter(region[0], inverse=True)[0] if region else ''
    deal = filters.deal_filter(deal, inverse=True) if deal else ''
    underground = filters.get_underground_station_by_id(underground) if underground else ''
    rooms = filters.rooms_filter(rooms, mode='array_to_str') if rooms else ''
    apartment_type = filters.apartment_type_filter(apartment_type, inverse=True) if apartment_type else ''
    if price:
        price = "{} руб. - {} руб.".format(int(price[0]), int(price[1]))
    else:
        price = ''

    msg = SEARCH_TERMS_ANSWER.format(
        city,
        deal,
        underground,
        rooms,
        apartment_type,
        price
    )
    return msg
