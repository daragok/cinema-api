from django.db import models


class TheaterRoom(models.Model):
    """ Theater room has rectangular shape and is defined by rows and seats count """
    name = models.CharField(max_length=20)
    rows_count = models.IntegerField()
    seats_per_row_count = models.IntegerField()
