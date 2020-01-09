class Offer:

    def __init__(self, offer_wrapper):
        self.offer_type = offer_wrapper['rel'] or 'internal'
        self.offer_class = 'promoted' if offer_wrapper.find('td', {'class': 'offer promoted '}) else 'standard'
        self.offer_link = offer_wrapper.find('a', {'data-cy': 'listing-ad-title'})['href']

