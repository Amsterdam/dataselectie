from rest_framework import routers

from datasets.bag import views as bagViews
from . import views as searchviews


class BagRouter(routers.DefaultRouter):
    """
    In Amsterdam is een systeem gerealiseerd voor het monitoren van deformatie (zakkingen). De oudere, vooroorlogse
    panden in Amsterdam zijn gebouwd op houten palen. De kwaliteit van deze fundering op houten palen verschilt sterk.
    Een slechte fundering kan zakkingen tot gevolg hebben, waardoor de kwaliteit van deze panden afneemt en
    mogelijkerwijs zelfs uiteindelijk tot sloop kan leiden.

    Om dergelijke zakkingen te kunnen volgen zijn op grote schaal meetbouten geplaatst in de binnenstad, de 19e eeuwse
    gordel en de gordel 20-40, grofweg alle gebieden binnen de ringweg. Met de meetgegevens wordt vooral het inzicht
    vergroot in grootte en snelheid van de zakking. Eigenaren van de panden kunnen met deze inzichten rekening houden
    bij mogelijke investeringen. De Registratie meetbouten is een initiatief van de afdeling Wonen (opdrachtgever), de
    bestuurscommissies en de afdeling Basisinformatie.
    """

    def get_api_root_view(self):
        view = super().get_api_root_view()
        cls = view.cls

        class Meetbouten(cls):
            pass

        Meetbouten.__doc__ = self.__doc__
        return Meetbouten.as_view()


meetbouten = MeetboutenRouter()

meetbouten.register(r'adressen', AdressenViewSet)
meetbouten.register(r'search', searchviews.SearchMeetboutViewSet, base_name='search')

