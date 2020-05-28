from collections import namedtuple


class Apartment:
    """Class to initialize apartment with his special parameters."""

    def __init__(self, region: str, deal: tuple, rooms: tuple = (1, 2), apartment_type: tuple = (True, True),
                 price: tuple = (None, None)):
        """
        Args:
            region (:str): Name of region for search.
                Available: 'Москва', 'Санкт-Петербург'.
            deal (:int): Deal type of apartment. There are four options:
                Available: 1 - for sale, 2 - for rent 1year+, 3 - rent 1year, 4 - per-day rent.
            rooms (:tuple of :int): List of available number of rooms for apartment.
                Available: 0 - studios, 1 - 1-room, 2 - 2-room, 3 - 3-room, 4 - 4-room+.
                Example: (1,2) - apartment with 1 or 2 rooms.
            apartment_type (:int): Apartment type.
                Available: 0 - all apartments, 1 - new apartments, 2 - secondary apartments.
            price (:tuple of :int or Nonetype): Min and max price of apartment.
                Example: (None, 3000000) - min price is None, max price is 3000000.
        """

        self.region = region
        self.deal = deal
        self.rooms = rooms
        self.apartment_type = apartment_type
        self.price = price
        self.region = region

    def create_link(self):
        query = r'https://cian.ru/cat.php?'
        for func in self.get_deal, self.get_region, self.get_rooms, self.get_apartment_type, self.get_price:
            query = func(query)
        return query

    def get_deal(self, query):
        if self.deal not in [1, 2, 3, 4]:
            raise ValueError('Incompatible arguments for Apartment.deal')

        if self.deal == 1:
            return query + '&' + 'deal_type=sale'
        else:
            if self.deal == 2:
                return query + '&' + 'deal_type=rent' + '&' + 'type=4'
            elif self.deal == 3:
                return query + '&' + 'deal_type=rent' + '&' + 'type=3'
            elif self.deal == 4:
                return query + '&' + 'deal_type=rent' + '&' + 'type=2'
            else:
                raise ValueError('No arguments for deal type.')

    def get_rooms(self, query):
        for n in list(self.rooms):
            if isinstance(n, int) and n > 0:
                query += '&' + 'room{}=1'.format(n)
            else:
                raise ValueError('Incompatible type of arguments for "rooms". Need tuple of int objects.')
        return query

    def get_apartment_type(self, query):
        if self.deal != 1 or self.apartment_type == 0:
            return query
        elif self.apartment_type == 1:
            return query + '&' + 'object_type=2'
        elif self.apartment_type == 2:
            return query + '&' + 'object_type=1'
        else:
            raise RuntimeError

    def get_price(self, query):
        if isinstance(self.price.min, int) and self.price.min <= self.price.max:
            query += '&' + 'minprice=' + str(self.price.min)

        if isinstance(self.price.max, int) and self.price.min <= self.price.max:
            query += '&' + 'maxprice=' + str(self.price.max)

        return query

    def get_region(self, query):
        if self.region == 'Москва':
            return query + '&' + 'region=1'
        elif self.region == 'Санкт-Петербург':
            return query + '&' + 'region=2'
        else:
            raise ValueError('Unsupported region.')


if __name__ == '__main__':
    ap = Apartment(region='Saint Petersburg', deal=(False, False, True, False), price=(0, 49900), apartment_type=(True, False))
    link = ap.create_link()
    print(link)
