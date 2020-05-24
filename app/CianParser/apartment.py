from collections import namedtuple


Deal = namedtuple('Deal', ['sale', 'rent_yearplus', 'rent_yearminus', 'rent_per_day'])
ApartmentType = namedtuple('ApartmentType', ['new', 'secondary'])
Price = namedtuple('Price', ['min', 'max'])


class Apartment:
    """Class to initialize apartment with his special parameters."""

    def __init__(self, region: str, deal: tuple, rooms: tuple = (1, 2), apartment_type: tuple = (True, True),
                 price: tuple = (None, None)):
        """
        Args:
            region (:str): Name of region for search.
                Example: Saint Petersburg.
            deal (:tuple of :bool): Deal type of apartment. There are four boolean options that can be combined:
                for sale or for rent 1year+, rent 1year- or per-day rent. # TODO исправить, тип может быть только один
                Example: (False, True, True, True) -  apartment's deal type is only for rent and per-day rent.
            rooms (:tuple of :int): List of available number of rooms for apartment.
                Example: (1,2) - apartment with 1 or 2 rooms.
            apartment_type (:tuple of :bool): New or secondary type of apartment.
                Example: (True, True) - apartment type is new or secondary.
            price (:tuple of :int or Nonetype): Min and max price of apartment.
                Example: (None, 3000000) - min price is None, max price is 3000000.
        """

        self.region = region
        self.deal = Deal(*deal)
        self.rooms = rooms
        self.apartment_type = ApartmentType(*apartment_type)
        self.price = Price(*price)
        self.region = region

    def create_link(self):
        query = r'https://cian.ru/cat.php?'
        for func in self.get_deal, self.get_region, self.get_rooms, self.get_apartment_type, self.get_price:
            query = func(query)
        return query

    def get_deal(self, query):
        if self.deal.sale and (self.deal.rent_yearplus or self.deal.rent_yearminus or self.deal.rent_per_day):
            raise ValueError('Incompatible arguments for object Deal.')

        if self.deal.sale:
            return query + '&' + 'deal_type=sale'
        else:
            if self.deal.rent_yearplus:
                return query + '&' + 'deal_type=rent' + '&' + 'type=4'
            elif self.deal.rent_yearminus:
                return query + '&' + 'deal_type=rent' + '&' + 'type=3'
            elif self.deal.rent_per_day:
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
        if not self.deal.sale or (self.apartment_type.new and self.apartment_type.secondary):
            return query
        elif self.apartment_type.new:
            return query + '&' + 'object_type=2'
        elif self.apartment_type.secondary:
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
        if self.region == 'Moscow':
            return query + '&' + 'region=1'
        elif self.region == 'Saint Petersburg':
            return query + '&' + 'region=2'
        else:
            raise ValueError('Unsupported region.')


if __name__ == '__main__':
    ap = Apartment(region='Saint Petersburg', deal=(False, False, True, False), price=(0, 49900), apartment_type=(True, False))
    link = ap.create_link()
    print(link)
