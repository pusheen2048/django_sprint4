from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class PublishedModel(models.Model):
    help_text_is_published = 'Снимите галочку, чтобы скрыть публикацию.'
    is_published = models.BooleanField('Опубликовано',
                                       help_text=help_text_is_published,
                                       default=True)
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        abstract = True


class Category(PublishedModel):
    title = models.CharField('Заголовок', max_length=256)
    description = models.TextField('Описание')
    help_text_slug = 'Идентификатор страницы для URL; \
разрешены символы латиницы, цифры, дефис и подчёркивание.'
    slug = models.SlugField('Идентификатор',
                            help_text=help_text_slug,
                            unique=True)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedModel):
    name = models.CharField('Название места', max_length=256)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(PublishedModel):
    title = models.CharField('Заголовок', max_length=256)
    text = models.TextField('Текст')
    help_text_pub_date = 'Если установить дату и время в будущем — \
можно делать отложенные публикации.'
    pub_date = models.DateTimeField('Дата и время публикации',
                                    help_text=help_text_pub_date)
    image = models.ImageField('Изображение',
                              upload_to='post_images',
                              null=True,
                              blank=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор публикации')
    location = models.ForeignKey(Location,
                                 on_delete=models.SET_NULL,
                                 verbose_name='Местоположение',
                                 null=True)
    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 verbose_name='Категория',
                                 null=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             verbose_name='Публикация',
                             related_name='comment')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор комментария',
                               related_name='comment')
    text = models.TextField('Текст комментария')
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at', )
