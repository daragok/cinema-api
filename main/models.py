from django.db import models


class TheaterRoom(models.Model):
    """ Theater room has rectangular shape and is defined by rows and seats count """

    name = models.CharField(max_length=20)
    rows_count = models.IntegerField()
    seats_per_row_count = models.IntegerField()

    def __str__(self):
        return self.name


class Movie(models.Model):
    TITLE_MAX_LENGTH = 100
    title = models.CharField(max_length=TITLE_MAX_LENGTH)
    duration_minutes = models.IntegerField()

    def __str__(self):
        return self.title


class Screening(models.Model):
    room = models.ForeignKey('TheaterRoom', on_delete=models.PROTECT)
    movie = models.ForeignKey('Movie', on_delete=models.PROTECT)
    start_time = models.DateTimeField()
    price = models.IntegerField()
