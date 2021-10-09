from tortoise import models, fields


class Poll(models.Model):
    id_poll = fields.IntField(pk=True)
    id_owner = fields.IntField(null=False)
    count_answer = fields.IntField(null=False)
    question = fields.CharField(max_length=255, null=False)
    answer_1 = fields.TextField(maxlenght=255, null=False)
    answer_2 = fields.TextField(maxlenght=255, null=False)
    answer_3 = fields.TextField(maxlenght=255, null=True)
    answer_4 = fields.TextField(maxlenght=255, null=True)
    answer_5 = fields.TextField(maxlenght=255, null=True)
    answer_6 = fields.TextField(maxlenght=255, null=True)


class Answer(models.Model):
    poll = fields.ForeignKeyField('models.Poll', related_name='answers')
    id_respondent = fields.IntField(null=False)
    id_answer = fields.IntField(null=False)
