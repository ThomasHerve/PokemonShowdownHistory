# Script to run to update the database
from typing import Dict, Tuple

import requests
import re
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pokemonstats.settings')
django.setup()
from stats.models import Month, Tier, Pokemon, PokemonMaster, TierPokemonMonth

month_regex = re.compile(r">(\d+\-\d+[-[0-z]*\/)")
tier_regex = re.compile(">([0-z]+-[0-z]*.txt)")
pokemon_regex = re.compile(r'((?P<rank>[0-9]+)[\s\|]+(?P<name>[A-z][A-z\-\s.]+)[\s]+\|[\s]+(?P<usage>[0-9.]+))')
url = "https://www.smogon.com/stats/"


def populate_pokemon(tier_url, tier_id):
    print(f"-- Creating tier {tier_url} : {tier_id}")
    response = str(requests.get(tier_url).content)
    pokemon_list = pokemon_regex.finditer(response)
    items = []
    for k in pokemon_list:
        _, rank, name, usage = k.groups()
        name = name.rstrip()
        # Master
        res, created = PokemonMaster.objects.update_or_create(
            name=name
        )
        # if created:
        #     add_image(res)

        p = Pokemon(
            rank=int(rank),
            name=name,
            usage=float(usage),
            tier_id=tier_id,
            master=res
        )
        items.append(p)

    return items


count = 0
if len(Tier.objects.all()) > 0:
    count = Tier.objects.latest('id').id

def count_id():
    global count
    count += 1
    return count


def pre_create_tier(month_name, month_object):
    tier_url = f"{url}/{month_name}"
    response = str(requests.get(tier_url).content)
    tier_list = tier_regex.findall(response)
    tier_list_ = []

    for tier in tier_list:
        if ("uber" in tier or "ou-" in tier or "uu-" in tier or "ru-" in tier or "nu-" in tier) and \
                ("gen" in tier
                 or (tier[1] == "u" and (tier[0] == "o" or tier[0] == "u" or tier[0] == "r" or tier[0] == "n"))
                 or (tier[0] == "u" and tier[0] == "b")):
            print(f"-- Creating tier {tier} - {month_name}")
            t = Tier(
                url=tier_url + "/" + tier,
                name=tier,
                month=month_object,
                id=count_id()
            )
            tier_list_.append(t)
    return tier_list_


def populate():
    # Months
    response = str(requests.get(url).content)
    month_list = month_regex.findall(response)
    month_list_objects = []
    tier_list = []
    pokemon_list = []

    c = 1
    m = Month.objects.latest('order').order
    if m:
        c = m

    for month in month_list:
        if Month.objects.filter(url=month).count() == 0:
            print(f"Creating month {month}")
            res, created = Month.objects.update_or_create(
                url=month,
                name=month,
                order=c
            )
            c += 1
            month_list_objects.append(res)
            t_l = pre_create_tier(month, res)
            tier_list.extend(t_l)

    print(f"Bulk create {len(tier_list)} tiers")
    Tier.objects.bulk_create(tier_list)

    for tier in tier_list:
        p_l = populate_pokemon(tier.url, tier.id)
        pokemon_list.extend(p_l)

    print(f"Bulk create {len(pokemon_list)} pokemons instance")
    Pokemon.objects.bulk_create(pokemon_list)

    add_all_last(month_list_objects)
    add_pokemon_tier(month_list_objects)


# Add OU

def add_last(tier_name, month_list_objects):
    ou_regex = re.compile(f"(gen(\d){tier_name}-)")

    for month in month_list_objects:
        # For each month
        print(f" -- Finding lasts in {month.name}")

        old_format = False

        # If recent format, retain the largest number
        most_recents = None
        most_recent_num = 0

        for tier in month.tier_set.all():
            # Is it in the old format ? last gen = no number
            if f"/{tier_name}-" in tier.url:
                if not old_format:
                    most_recents = [tier]
                    old_format = True
                else:
                    most_recents.append(tier)
                continue

            if not old_format and len(ou_regex.findall(tier.url)) > 0:
                num = int(re.search(f"(gen(\d){tier_name}-)", tier.url).groups()[1])
                if num == most_recent_num:
                    most_recents.append(tier)
                elif num > most_recent_num:
                    most_recent_num = num
                    most_recents = [tier]

        for tier in most_recents:
            tier.is_last = True
            tier.category = tier_name
            c = 0
            while tier.name[c] != "-":
                c += 1
            temp_elo = tier.name[c + 1:]
            tier.elo = int(temp_elo[:len(temp_elo) - 4])
            tier.save()


def add_all_last(month_list_objects):
    for k in ["ou", "uu", "ru", "nu", "ubers"]:
        print(f"Tier : {k}")
        add_last(k, month_list_objects)


def add_pokemon_instance():
    print("Starting add pokemon master")
    masters = {}
    for k in PokemonMaster.objects.all():
        masters[k.name] = k
        print(" -- Add " + k.name)
        Pokemon.objects.filter(name=k.name).update(master=k)


tiers_value = {
    "ubers": 5,
    "ou": 4,
    "uu": 3,
    "ru": 2,
    "nu": 1
}


# Check if tier a < tier b
def _compare_tier(a: str, b: str) -> bool:
    a_real = None
    b_real = None
    if "ubers" in a:
        a_real = "ubers"
    elif "ou" in a:
        a_real = "ou"
    elif "uu" in a:
        a_real = "uu"
    elif "ru" in a:
        a_real = "ru"
    elif "nu" in a:
        a_real = "nu"
    if "ubers" in b:
        b_real = "ubers"
    elif "ou" in b:
        b_real = "ou"
    elif "uu" in b:
        b_real = "uu"
    elif "ru" in b:
        b_real = "ru"
    elif "nu" in b:
        b_real = "nu"
    return tiers_value[a_real] < tiers_value[b_real]


def add_pokemon_tier(month_list_objects):
    print("Start find tier of pokemons each month")
    pokemon_month: Dict[Tuple[PokemonMaster, Month], Tier] = {}
    query = Pokemon.objects.filter(tier__is_last=True).filter(tier__month__in=month_list_objects)
    total = query.count()
    c = 0
    for k in query:
        if (k.master, k.tier.month) in pokemon_month.keys():
            if _compare_tier(k.tier.name, pokemon_month[(k.master, k.tier.month)].name) and \
                    k.tier.elo > pokemon_month[(k.master, k.tier.month)].elo:
                pokemon_month[(k.master, k.tier.month)] = k.tier
        else:
            pokemon_month[(k.master, k.tier.month)] = k.tier
        c += 1
        print(f" -- {c / total * 100}%")
    print("Generate each database object from dict")
    tpm_list = []
    for (p, m), t in pokemon_month.items():
        tpm_list.append(
            TierPokemonMonth(
                pokemon=p,
                tier=t,
                month=m
            )
        )
    print("Start bulk create")
    TierPokemonMonth.objects.bulk_create(tpm_list)


populate()
# add_all_last()
# add_pokemon_instance()
# add_pokemon_tier(Month.objects.all())
