from django.db import models


class Person(models.Model):
    ROLE_ADMIN = 'admin'
    ROLE_TEACHER = 'teacher'
    ROLE_STUDENT = 'student'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_TEACHER, 'Teacher'),
        (ROLE_STUDENT, 'Student'),
    ]

    surname = models.CharField(max_length=50)
    login = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    group = models.CharField(max_length=50, blank=True)
    class_name = models.CharField(max_length=50, blank=True)
    student_id = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    parent_name = models.CharField(max_length=100, blank=True)
    birthday = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.surname} ({self.role})"

    def total_points(self):
        return self.received_points.aggregate(total=models.Sum('amount'))['total'] or 0

    def total_tokens(self):
        return self.received_tokens.count()


class PointAward(models.Model):
    teacher = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='given_points',
        limit_choices_to={'role': Person.ROLE_TEACHER},
    )
    student = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='received_points',
        limit_choices_to={'role': Person.ROLE_STUDENT},
    )
    amount = models.PositiveIntegerField()
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher.surname} → {self.student.surname}: {self.amount}"


class TokenAward(models.Model):
    teacher = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='given_tokens',
        limit_choices_to={'role': Person.ROLE_TEACHER},
    )
    student = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='received_tokens',
        limit_choices_to={'role': Person.ROLE_STUDENT},
    )
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher.surname} → {self.student.surname} token"
