from django.shortcuts import render, redirect
from stats.models import *


# Create your views here.

def home(request):
    pokemon_list = get_pokemon_list()
    return render(request, 'html/home.html', locals())


def pokemon(request, name):
    name_valid = PokemonMaster.objects.filter(name=name)
    if len(name_valid) == 0:
        return redirect(home)

    pokemon_list = get_pokemon_list()
    url: str = name
    # Image
    if url.startswith('Pikachu-') and (
            url.endswith("Belle") or url.endswith("Libre") or url.endswith("Partner") or url.endswith(
        "Phd") or url.endswith("Pop-Star")):
        url = 'pikachu'
    elif url.startswith('Pikachu-'):
        url += '-cap'
    elif url.endswith('Alola'):
        url += 'n'
    elif url.endswith('Galar'):
        url += "ian"
    elif url.endswith('-Gmax'):
        url = url[:-4] + 'gigantamax'
    url = url.lower()

    # Tiers
    _tiers = [k.month.name[:-1] + " " + str(tier_to_number(k.tier.category)) for k in
              TierPokemonMonth.objects.filter(pokemon__name=name)]
    tiers = ','.join(_tiers)

    # Usages
    # FLEMME D'ECRIRE DU CODE PROPRE
    usages = {}
    for k in ["ubers", "ou", "uu", "ru", "nu"]:
        usages[k] = {}
        usages[k]["0"] = ','.join([(k.tier.month.name[:-1] + " " + str(k.usage)) for k in
                                   Pokemon.objects.filter(name=name, tier__category=k, tier__elo=0)])
        usages[k]["1500"] = ','.join([(k.tier.month.name[:-1] + " " + str(k.usage)) for k in
                                      Pokemon.objects.filter(name=name, tier__category=k, tier__elo=1500)])
        usages[k]["1600"] = ','.join([(k.tier.month.name[:-1] + " " + str(k.usage)) for k in
                                      Pokemon.objects.filter(name=name, tier__category=k, tier__elo__in=[1630, 1695])])
        usages[k]["1800"] = ','.join([(k.tier.month.name[:-1] + " " + str(k.usage)) for k in
                                      Pokemon.objects.filter(name=name, tier__category=k, tier__elo__in=[1760, 1825])])

    return render(request, 'html/pokemon.html', locals())


def get_pokemon_list():
    return ','.join([k.name for k in PokemonMaster.objects.all()])


def tier_to_number(tier):
    if tier == "ubers":
        return 5
    if tier == "ou":
        return 4
    if tier == "uu":
        return 3
    if tier == "ru":
        return 2
    return 1
