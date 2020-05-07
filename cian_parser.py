from collections import namedtuple


class CianParser:
    def __init__(self):
        pass


Deal = namedtuple('Deal', ['sale', 'rent_yearplus', 'rent_yearminus', 'rent_per_day'])
ApartmentType = namedtuple('ApartmentType', ['new', 'secondary'])
Price = namedtuple('Price', ['min', 'max'])


class Apartment:
    """Class to initialize apartment with his special parameters."""


    def __init__(self, deal: tuple, rooms: tuple, apartment_type: tuple = (True, True), price: tuple = (None, None),
                 ):
        """
        Args:
            deal (:tuple of :bool): Deal type of apartment. There are four boolean options that can be combined:
                for sale or for rent 1year+, rent 1year- or per-day rent.
                Example: (False, True, True) -  apartment's deal type is only for rent and per-day rent.
            rooms (:tuple of :int): List of available number of rooms for apartment.
                Example: (1,2) - apartment with 1 or 2 rooms.
            apartment_type (:tuple of :bool): New or secondary type of apartment.
                Example: (True, True) - apartment type is new or secondary.
            price (:tuple of :int or Nonetype): Min and max price of apartment.
                Example: (None, 3000000) - min price is None, max price is 3000000.
        """
        self.deal = Deal(*deal)
        self.rooms = rooms
        self.apartment_type = ApartmentType(*apartment_type)
        self.price = Price(*price)

    def get_deal(self, query):
        if self.deal.sale and (self.deal.rent_yearplus or self.deal.rent_yearminus or self.deal.rent_per_day):
            raise ValueError('Incompatible arguments for object Deal.')

        if self.deal.sale:
            return 'deal_type=sale' + '&' + query
        else:
            if self.deal.rent_yearplus:
                return 'deal_type=rent' + '&' + query + '&' + 'type=4'
            elif self.deal.rent_yearminus:
                return 'deal_type=rent' + '&' + query + '&' + 'type=3'
            elif self.deal.rent_per_day:
                return 'deal_type=rent' + '&' + query + '&' + 'type=2'
            else:
                raise ValueError('No arguments for deal type.')

    def create_link(self):
        #t = r'https://spb.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&room1=1&room2=1'
        pass


if __name__ == '__main__':
    pass
