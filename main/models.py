from django.db import models
from PIL import Image, ImageOps 
from io import BytesIO
from django.core.files.base import ContentFile
import os


class Project(models.Model):
    """Модель для проектов портфолио"""
    class Category(models.TextChoices):
        LANDING = 'landing', 'Лендинги'
        ECOMMERCE = 'ecommerce', 'Интернет-магазины'
        CORPORATE = 'corporate', 'Корпоративные сайты'
        WEBAPP = 'webapp', 'Веб-сервисы'

    title = models.CharField('Название', max_length=200)
    category = models.CharField('Категория', max_length=50, choices=Category.choices, default=Category.LANDING)
    description = models.TextField('Описание')
    overlay_text = models.CharField('Текст поверх слайда', max_length=255, blank=True, help_text='Текст, который будет печататься над активным слайдом (например: "Создайте сайт для...")')
    brief_text = models.TextField('Текст ТЗ', blank=True, help_text='Текст технического задания, который показывается над активной карточкой (например: "ТЗ: Создайте сайт бухгалтерского учета для малого бизнеса")')
    image = models.ImageField('Изображение', upload_to='projects/')
    thumbnail = models.ImageField('Превью WebP', upload_to='projects/thumbs/', blank=True)
    thumbnail_avif = models.ImageField('Превью AVIF', upload_to='projects/thumbs/', blank=True)
    video = models.FileField('Видео (mp4)', upload_to='projects/videos/', blank=True, null=True)
    url = models.URLField('URL проекта', blank=True)
    tags = models.CharField('Теги', max_length=255, blank=True)
    order = models.IntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    # SEO Fields
    seo_title = models.CharField('SEO Title', max_length=255, blank=True, help_text='Если пусто, используется название проекта')
    seo_description = models.TextField('SEO Description', blank=True, help_text='Если пусто, используется описание проекта')

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Если изображение есть, а превью нет - создаем
        if self.image and not self.thumbnail:
            try:
                self.create_thumbnail()
            except Exception as e:
                print(f"Error creating thumbnail: {e}")
        
        super().save(*args, **kwargs)

    def create_thumbnail(self):
        if not self.image:
            return

        try:
            # Открываем изображение
            img = Image.open(self.image)

            # Конвертируем в RGB если нужно
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # Физические размеры для превью (например, ширина 800px)
            base_width = 800
            # 1. Сначала ресайз по ширине до 800px (если больше)
            if img.width > base_width:
                w_percent = (base_width / float(img.size[0]))
                h_size = int((float(img.size[1]) * float(w_percent)))
                img = img.resize((base_width, h_size), Image.Resampling.LANCZOS)
            elif img.width < base_width:
                base_width = img.width

            # 2. Обрезка (Crop) по высоте под соотношение 16:10 (как в CSS)
            target_height = int(base_width / 1.6) # Например, 800 / 1.6 = 500px

            if img.height > target_height:
                # Обрезаем: (left, top, right, bottom)
                # Берем только верхнюю часть
                img = img.crop((0, 0, base_width, target_height))

            # Сохраняем оптимизированную WebP версию
            thumb_io = BytesIO()
            img.save(thumb_io, format='WEBP', quality=85, method=6)  # method=6 для лучшей компрессии

            # Генерируем имя файла
            name = os.path.basename(self.image.name)
            name_without_ext = os.path.splitext(name)[0]
            thumb_name = f"{name_without_ext}_thumb.webp"

            # Сохраняем WebP в поле thumbnail
            self.thumbnail.save(thumb_name, ContentFile(thumb_io.getvalue()), save=False)

            # Для совместимости, копируем WebP в поле thumbnail_avif (пока без настоящего AVIF)
            # В будущем можно добавить поддержку AVIF через pillow-avif
            self.thumbnail_avif.save(thumb_name, ContentFile(thumb_io.getvalue()), save=False)

        except Exception as e:
            # Если файл не найден или ошибка - пропускаем
            print(f"Thumbnail creation error: {e}")


class ProjectImage(models.Model):
    """Дополнительные фото для проекта"""
    project = models.ForeignKey(Project, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField('Изображение', upload_to='projects/gallery/')
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Фото проекта'
        verbose_name_plural = 'Фото проектов'
        ordering = ['order']

    def __str__(self):
        return f'Фото для {self.project.title}'


class Service(models.Model):
    """Услуги студии"""
    title = models.CharField('Название', max_length=150)
    slug = models.SlugField('Слаг', unique=True, max_length=180)
    summary = models.TextField('Короткое описание')
    description = models.TextField('Подробное описание', blank=True, help_text='Детальное описание услуги для страницы услуг')
    process = models.TextField('Процесс работы', blank=True, help_text='Этапы работы над проектом')
    technologies = models.TextField('Технологии', blank=True, help_text='Используемые технологии и инструменты')
    benefits = models.TextField('Преимущества', blank=True, help_text='Почему выбрать эту услугу')
    deliverables = models.TextField('Что включено')
    timeline = models.CharField('Сроки', max_length=100)
    price_from = models.PositiveIntegerField('Стоимость от, ₽', default=0)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать', default=True)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class ProjectCase(models.Model):
    """Подробные кейсы"""
    project = models.ForeignKey(Project, verbose_name='Проект', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField('Название кейса', max_length=200)
    slug = models.SlugField('Слаг', unique=True, max_length=200)
    client = models.CharField('Клиент', max_length=150, blank=True)
    industry = models.CharField('Индустрия', max_length=150, blank=True)
    summary = models.TextField('Сводка', help_text='Короткое описание проекта')
    challenge = models.TextField('Контекст и вызов')
    goals = models.TextField('Цели клиента', blank=True)
    solution = models.TextField('Наше решение')
    stack = models.TextField('Технологический стек', blank=True)
    metrics = models.TextField('Ключевые метрики', blank=True)
    result = models.TextField('Результат', blank=True)
    hero_image = models.ImageField('Главное изображение', upload_to='cases/hero/')
    thumbnail = models.ImageField('Превью', upload_to='cases/thumbs/')
    quote = models.TextField('Отзыв клиента', blank=True)
    quote_author = models.CharField('Автор отзыва', max_length=150, blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_featured = models.BooleanField('Показывать на главной', default=False)
    published_at = models.DateField('Дата релиза', blank=True, null=True)
    
    # SEO Fields
    seo_title = models.CharField('SEO Title', max_length=255, blank=True, help_text='Если пусто, используется название кейса')
    seo_description = models.TextField('SEO Description', blank=True, help_text='Если пусто, используется сводка (summary)')

    class Meta:
        verbose_name = 'Кейс'
        verbose_name_plural = 'Кейсы'
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('index') + '#portfolio'


class Industry(models.Model):
    """Приоритетные индустрии"""
    name = models.CharField('Название отрасли', max_length=150)
    slug = models.SlugField('Слаг', unique=True, max_length=180)
    description = models.TextField('Описание', blank=True)
    pain_points = models.TextField('Боли рынка')
    solution = models.TextField('Как решаем')
    order = models.PositiveIntegerField('Порядок', default=0)
    related_cases = models.ManyToManyField(ProjectCase, verbose_name='Кейсы', blank=True, related_name='industries')

    class Meta:
        verbose_name = 'Индустрия'
        verbose_name_plural = 'Индустрии'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель для отзывов клиентов"""
    client_name = models.CharField('Имя клиента', max_length=100)
    client_position = models.CharField('Должность', max_length=100)
    text = models.TextField('Текст отзыва')
    rating = models.IntegerField('Оценка', default=5)
    order = models.IntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['order', '-created_at']

    def __str__(self):
        return f'{self.client_name} - {self.rating}/5'


class Question(models.Model):
    """Модель для частых вопросов (FAQ)"""
    question = models.CharField('Вопрос', max_length=255)
    answer = models.TextField('Ответ')
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать', default=True)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['order']

    def __str__(self):
        return self.question


def team_photo_upload_to(instance, filename):
    """Функция для загрузки фото членов команды с нормализацией имен"""
    import os
    from django.utils.text import slugify

    # Получаем расширение файла
    ext = os.path.splitext(filename)[1].lower()

    # Создаем нормализованное имя файла на основе имени члена команды
    safe_name = slugify(instance.name).replace('-', '_')
    new_filename = f"photo_{safe_name}{ext}"

    return f"team/{new_filename}"


class TeamMember(models.Model):
    """Модель для членов команды"""
    name = models.CharField('Имя', max_length=100)
    position = models.CharField('Должность', max_length=100)
    photo = models.ImageField('Фото', upload_to=team_photo_upload_to)
    bio = models.TextField('Биография')
    specialization = models.TextField('Специализация', blank=True, help_text='Навыки через запятую или точку с запятой')
    experience = models.CharField('Опыт работы', max_length=100, blank=True, help_text='Например: 6 лет')
    is_featured = models.BooleanField('Показывать на главной', default=False)
    order = models.IntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Член команды'
        verbose_name_plural = 'Команда'
        ordering = ['order']

    def __str__(self):
        return self.name

    @property
    def skills_list(self):
        if not self.specialization:
            return []
        import re
        return [s.strip() for s in re.split(r'[•,;\n]', self.specialization) if s.strip()]


class Lead(models.Model):
    """Модель для заявок с формы обратной связи"""

    class Source(models.TextChoices):
        MAIN = ('main', 'Главная')
        SERVICES = ('services', 'Услуги')
        CASES = ('cases', 'Кейсы')
        INDUSTRIES = ('industries', 'Индустрии')
        FOOTER = ('footer', 'Футер')

    class Status(models.TextChoices):
        NEW = ('new', 'Новая')
        IN_PROGRESS = ('in_progress', 'В работе')
        WON = ('won', 'Выиграна')
        LOST = ('lost', 'Закрыта')

    name = models.CharField('Имя', max_length=100)
    company = models.CharField('Компания', max_length=150, blank=True)
    email = models.EmailField('Email', blank=True)
    phone = models.CharField('Телефон', max_length=20)
    project_type = models.CharField('Тема / Тип сайта', max_length=255, blank=True)
    budget = models.CharField('Бюджет', max_length=100, blank=True)
    message = models.TextField('Сообщение', blank=True)
    source = models.CharField('Источник', max_length=20, choices=Source.choices, default=Source.MAIN)
    status = models.CharField('Статус', max_length=20, choices=Status.choices, default=Status.NEW)
    manager_note = models.TextField('Комментарий менеджера', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.email}'


class WebsiteType(models.Model):
    title = models.CharField('Название', max_length=150)
    slug = models.SlugField('URL (slug)', max_length=150, unique=True, blank=True, help_text='Автоматически генерируется из названия')
    description = models.TextField('Краткое описание', help_text='Для карточки на главной')
    detailed_description = models.TextField('Детальное описание', blank=True, help_text='Для страницы типа сайта')
    subtitle = models.CharField('Подзаголовок', max_length=255, blank=True, help_text='Дополнительное описание (опционально)')
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать', default=True)
    is_featured = models.BooleanField('Выделить', default=False, help_text='Карточка на всю ширину с темным фоном')

    # SEO Fields
    seo_title = models.CharField('SEO Title', max_length=255, blank=True, help_text='Если пусто, используется название типа')
    seo_description = models.TextField('SEO Description', blank=True, help_text='Если пусто, используется краткое описание')

    class Meta:
        verbose_name = 'Тип сайта'
        verbose_name_plural = 'Типы сайтов'
        ordering = ['order']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('index') + '#contact'

    @property
    def price_from(self):
        """Возвращает стоимость из первой опции"""
        first_option = self.pricing_options.order_by('order').first()
        if first_option:
            return first_option.price
        return None

    @property
    def time_estimate(self):
        """Возвращает сроки из первой опции"""
        first_option = self.pricing_options.order_by('order').first()
        if first_option:
            return first_option.time_estimate
        return None

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            try:
                from transliterate import translit
                transliterated = translit(self.title, 'ru', reversed=True)
                self.slug = slugify(transliterated)
            except (ImportError, Exception):
                self.slug = slugify(self.title, allow_unicode=True)
                if not self.slug:
                    # Final fallback if slug is still empty
                    import uuid
                    self.slug = str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)


class WebsiteTypeOption(models.Model):
    website_type = models.ForeignKey(WebsiteType, on_delete=models.CASCADE, related_name='pricing_options', verbose_name='Тип сайта')
    service_name = models.CharField('Название услуги', max_length=255)
    description = models.TextField('Описание', blank=True)
    time_estimate = models.CharField('Срок выполнения', max_length=100, blank=True, help_text='Например: 5-7 дней')
    price = models.CharField('Стоимость', max_length=100, help_text='Например: от 50 000 ₽')
    order = models.IntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Опция расценок'
        verbose_name_plural = 'Опции расценок'
        ordering = ['website_type', 'order']

    def __str__(self):
        return f'{self.website_type.title} - {self.service_name}'


class ActiveOrder(models.Model):
    """Консультации (активные заказы для канбан-доски)"""
    
    class Status(models.TextChoices):
        ACCEPTED = 'accepted', 'Принятые в работу'
        IN_PROGRESS = 'in_progress', 'В работе'
        TESTING = 'testing', 'Тестирование'
        COMPLETED = 'completed', 'Завершенные'

    title = models.CharField('Название проекта', max_length=200)
    description = models.TextField('Описание')
    status = models.CharField('Статус', max_length=20, choices=Status.choices, default=Status.ACCEPTED)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Консультация'
        verbose_name_plural = 'Консультации'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ActiveOrderFile(models.Model):
    """Файлы для активного заказа"""
    
    class FileType(models.TextChoices):
        IMAGE = 'image', 'Изображение'
        DOCUMENT = 'document', 'Документ'

    order = models.ForeignKey(ActiveOrder, related_name='files', on_delete=models.CASCADE)
    file = models.FileField('Файл', upload_to='orders/files/')
    file_type = models.CharField('Тип', max_length=20, choices=FileType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Файл заказа'
        verbose_name_plural = 'Файлы заказа'
