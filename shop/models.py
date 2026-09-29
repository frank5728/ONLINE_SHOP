from django.db import models


class Size(models.Model):

    name = models.CharField(
        max_length=20
    )

    def __str__(self):
        return self.name


class Product(models.Model):

    name = models.CharField(
        max_length=100
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True
    )

    sizes = models.ManyToManyField(
        Size
    )

    def __str__(self):
        return self.name


class Order(models.Model):

    order_reference = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    customer_name = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=20
    )

    location = models.CharField(
        max_length=200
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    size = models.ForeignKey(
        Size,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        if not self.order_reference:

            self.order_reference = f"ORD-{self.id:05d}"

            super().save(
                update_fields=["order_reference"]
            )

    def __str__(self):

        return self.order_reference or self.customer_name