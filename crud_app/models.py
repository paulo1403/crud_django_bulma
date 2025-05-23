from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    STATUS_CHOICES = [
        ("todo", "To Do"),
        ("in_progress", "In Progress"),
        ("done", "Done"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="items")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to="item_files/", null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name="items", blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="todo")

    # Este es un comentario para forzar la detección de cambios

    def __str__(self):
        return self.name

    def file_extension(self):
        if self.file:
            name = self.file.name
            return name.split(".")[-1].lower() if "." in name else ""
        return ""

    def is_image(self):
        ext = self.file_extension()
        return ext in ["jpg", "jpeg", "png", "gif", "bmp", "webp"]


class ChangeLog(models.Model):
    ACTION_CHOICES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
    ]

    item = models.ForeignKey(
        Item, on_delete=models.SET_NULL, related_name="change_logs", null=True
    )
    item_name = models.CharField(
        max_length=100, blank=True
    )  # Guarda el nombre del ítem para referencia
    original_item_id = models.IntegerField(
        default=0
    )  # Guarda el ID del ítem para referencia
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    additional_data = models.JSONField(
        blank=True, null=True
    )  # Para guardar datos adicionales si es necesario

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        item_name = self.item.name if self.item else self.item_name
        username = self.user.username if self.user else "Unknown user"
        return f"{self.action.capitalize()} - {item_name} by {username} on {self.timestamp}"


class Comment(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.item.name}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="favorited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "user",
            "item",
        )  # Evitar duplicados - un usuario solo puede marcar como favorito una vez

    def __str__(self):
        return f"{self.user.username}'s favorite: {self.item.name}"
