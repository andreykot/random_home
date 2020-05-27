from app import handlers, filters, buttons


def set_routes(dp):
    dp.register_message_handler(handlers.start, commands=['start'])
    dp.register_message_handler(handlers.__test_flats_searching, commands=['test'])

    dp.register_message_handler(handlers.search_terms, commands=['search_terms'])
    dp.register_message_handler(handlers.get_city, commands=['city'])
    dp.register_message_handler(handlers.get_deal_type, commands=['deal'])
    dp.register_message_handler(handlers.get_rooms, commands=['rooms'])
    dp.register_message_handler(handlers.get_apartment_type, commands=['type'])
    dp.register_message_handler(handlers.get_price, commands=['price'])

    dp.register_callback_query_handler(handlers.callback_search_terms_main,
                                       text='Задать критерии поиска')
    dp.register_callback_query_handler(handlers.callback_search_terms,
                                       filters.search_terms)
    dp.register_callback_query_handler(handlers.callback_get_city,
                                       lambda query: query.data in buttons.CITY.items)
    dp.register_callback_query_handler(handlers.callback_get_deal_type,
                                       lambda query: query.data in buttons.DEAL_TYPE.items)
    dp.register_callback_query_handler(handlers.callback_get_rooms,
                                       lambda query: query.data in buttons.ROOMS.items)
    dp.register_callback_query_handler(handlers.callback_get_apartment_type,
                                       lambda query: query.data in buttons.APARTMENT_TYPE.items)
    dp.register_callback_query_handler(handlers.callback_get_price,
                                       lambda query: query.data in buttons.PRICE['rent'].items + buttons.PRICE['sale'].items)

