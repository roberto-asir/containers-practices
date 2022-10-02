from django.db import models



class games_counter(models.Model):
    player = models.PositiveIntegerField()
    pc = models.PositiveIntegerField()
