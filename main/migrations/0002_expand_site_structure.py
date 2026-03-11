from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='tags',
            field=models.CharField(blank=True, max_length=255, verbose_name='Теги'),
        ),
        migrations.CreateModel(
            name='ProjectCase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название кейса')),
                ('slug', models.SlugField(max_length=200, unique=True, verbose_name='Слаг')),
                ('client', models.CharField(blank=True, max_length=150, verbose_name='Клиент')),
                ('industry', models.CharField(blank=True, max_length=150, verbose_name='Индустрия')),
                ('summary', models.TextField(help_text='Короткое описание проекта', verbose_name='Сводка')),
                ('challenge', models.TextField(verbose_name='Контекст и вызов')),
                ('goals', models.TextField(blank=True, verbose_name='Цели клиента')),
                ('solution', models.TextField(verbose_name='Наше решение')),
                ('stack', models.TextField(blank=True, verbose_name='Технологический стек')),
                ('metrics', models.TextField(blank=True, verbose_name='Ключевые метрики')),
                ('result', models.TextField(blank=True, verbose_name='Результат')),
                ('hero_image', models.ImageField(upload_to='cases/hero/', verbose_name='Главное изображение')),
                ('thumbnail', models.ImageField(upload_to='cases/thumbs/', verbose_name='Превью')),
                ('quote', models.TextField(blank=True, verbose_name='Отзыв клиента')),
                ('quote_author', models.CharField(blank=True, max_length=150, verbose_name='Автор отзыва')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('is_featured', models.BooleanField(default=False, verbose_name='Показывать на главной')),
                ('published_at', models.DateField(blank=True, null=True, verbose_name='Дата релиза')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to='main.project', verbose_name='Проект')),
            ],
            options={
                'verbose_name': 'Кейс',
                'verbose_name_plural': 'Кейсы',
                'ordering': ['order', 'title'],
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150, verbose_name='Название')),
                ('slug', models.SlugField(max_length=180, unique=True, verbose_name='Слаг')),
                ('summary', models.TextField(verbose_name='Короткое описание')),
                ('deliverables', models.TextField(verbose_name='Что включено')),
                ('timeline', models.CharField(max_length=100, verbose_name='Сроки')),
                ('price_from', models.PositiveIntegerField(default=0, verbose_name='Стоимость от, ₽')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('is_active', models.BooleanField(default=True, verbose_name='Показывать')),
            ],
            options={
                'verbose_name': 'Услуга',
                'verbose_name_plural': 'Услуги',
                'ordering': ['order', 'title'],
            },
        ),
        migrations.CreateModel(
            name='Industry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Название отрасли')),
                ('slug', models.SlugField(max_length=180, unique=True, verbose_name='Слаг')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('pain_points', models.TextField(verbose_name='Боли рынка')),
                ('solution', models.TextField(verbose_name='Как решаем')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('related_cases', models.ManyToManyField(blank=True, related_name='industries', to='main.projectcase', verbose_name='Кейсы')),
            ],
            options={
                'verbose_name': 'Индустрия',
                'verbose_name_plural': 'Индустрии',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.AddField(
            model_name='lead',
            name='budget',
            field=models.CharField(choices=[('lt500', 'до 500 тыс ₽'), ('500-1500', '500 тыс — 1.5 млн ₽'), ('1500-3000', '1.5 — 3 млн ₽'), ('gt3000', '3+ млн ₽')], default='lt500', max_length=20, verbose_name='Бюджет'),
        ),
        migrations.AddField(
            model_name='lead',
            name='company',
            field=models.CharField(blank=True, max_length=150, verbose_name='Компания'),
        ),
        migrations.AddField(
            model_name='lead',
            name='manager_note',
            field=models.TextField(blank=True, verbose_name='Комментарий менеджера'),
        ),
        migrations.AddField(
            model_name='lead',
            name='project_type',
            field=models.CharField(choices=[('mvp', 'MVP / стартап'), ('ecommerce', 'E-commerce / магазин'), ('corporate', 'Корпоративный сайт'), ('platform', 'Платформа / портал'), ('support', 'Сопровождение/поддержка'), ('other', 'Другое')], default='mvp', max_length=50, verbose_name='Тип проекта'),
        ),
        migrations.AddField(
            model_name='lead',
            name='source',
            field=models.CharField(choices=[('main', 'Главная'), ('services', 'Услуги'), ('cases', 'Кейсы'), ('industries', 'Индустрии'), ('footer', 'Футер')], default='main', max_length=20, verbose_name='Источник'),
        ),
        migrations.AddField(
            model_name='lead',
            name='status',
            field=models.CharField(choices=[('new', 'Новая'), ('in_progress', 'В работе'), ('won', 'Выиграна'), ('lost', 'Закрыта')], default='new', max_length=20, verbose_name='Статус'),
        ),
        migrations.AddField(
            model_name='lead',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now, verbose_name='Дата обновления'),
            preserve_default=False,
        ),
    ]


