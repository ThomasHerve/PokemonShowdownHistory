from django.db import models


class Month(models.Model):
    url = models.CharField(max_length=1000, primary_key=True)
    name = models.CharField(max_length=1000)
    order = models.IntegerField()

    def __str__(self):
        return f"{self.name}"


class Tier(models.Model):
    url = models.CharField(max_length=1000)
    name = models.CharField(max_length=1000)
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    is_last = models.BooleanField(default=False)
    category = models.CharField(default=None, max_length=15, null=True)
    elo = models.IntegerField(default=None, null=True)

    class Meta:
        unique_together = (("url", "month"),)

    def __str__(self):
        return f"{self.month} - {self.name}"


class PokemonMaster(models.Model):
    name = models.CharField(max_length=1000, primary_key=True)

    def __str__(self):
        return self.name


class Pokemon(models.Model):
    rank = models.IntegerField()
    usage = models.FloatField()
    name = models.CharField(max_length=1000)
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE)
    master = models.ForeignKey(PokemonMaster, on_delete=models.CASCADE, default=None, null=True)

    class Meta:
        unique_together = (("name", "tier"),)

    def __str__(self):
        return f"{self.tier} - {self.name}"


# Class which say which tier a pokemon is each month
class TierPokemonMonth(models.Model):
    pokemon = models.ForeignKey(PokemonMaster, on_delete=models.CASCADE)
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE)
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
