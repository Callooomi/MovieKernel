from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Quiz(models.Model):
    """A quiz. Each quiz is a single type: every question is multiple choice,
    or every question is click-to-reveal."""

    MULTIPLE_CHOICE = 'mc'
    REVEAL = 'reveal'
    TYPE_CHOICES = [
        (MULTIPLE_CHOICE, 'Multiple choice'),
        (REVEAL, 'Click to reveal'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=220, unique=True, blank=True,
        help_text="Leave blank to auto-generate from the title.",
    )
    headline = models.CharField(
        max_length=300, blank=True,
        help_text="Short teaser shown under the title on the quizzes feed.",
    )
    tag = models.CharField(
        max_length=60, blank=True,
        help_text="Optional category chip, e.g. 'Trivia' or 'Hard mode'.",
    )
    quiz_type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default=MULTIPLE_CHOICE,
        help_text="Multiple choice (click an option, right=green/wrong=red) "
                  "or click-to-reveal (a button shows the answer).",
    )
    hero_image = models.ImageField(
        upload_to='quizzes/heroes/', blank=True, null=True,
        help_text="Image shown on the feed card and at the top of the quiz.",
    )
    is_published = models.BooleanField(
        default=False,
        help_text="Untick to keep this as a draft (hidden from the site).",
    )
    published_at = models.DateTimeField(
        default=timezone.now,
        help_text="Quizzes are ordered newest-first by this date.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']
        verbose_name_plural = 'quizzes'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200] or 'quiz'
            slug = base
            n = 2
            while Quiz.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('quizzes:detail', kwargs={'slug': self.slug})

    @property
    def is_multiple_choice(self):
        return self.quiz_type == self.MULTIPLE_CHOICE


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers show first.")
    text = models.TextField(help_text="The question.")
    image = models.ImageField(
        upload_to='quizzes/questions/', blank=True, null=True,
        help_text="Optional image shown below the question.",
    )

    # --- Multiple-choice questions: fill these two in ---
    options = models.TextField(
        blank=True,
        help_text="Multiple choice only: type the options, ONE PER LINE.",
    )
    correct_option = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Multiple choice only: which option line is correct? "
                  "1 = first line, 2 = second line, and so on.",
    )

    # --- Click-to-reveal questions: fill this in ---
    reveal_answer = models.TextField(
        blank=True,
        help_text="Click-to-reveal only: the answer shown when the button is pressed.",
    )

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return (self.text[:60] + '…') if len(self.text) > 60 else self.text

    @property
    def option_lines(self):
        """The options as a clean list (blank lines ignored)."""
        return [ln.strip() for ln in self.options.splitlines() if ln.strip()]

    @property
    def choice_list(self):
        """List of {'text', 'is_correct'} for rendering multiple-choice buttons."""
        return [
            {'text': opt, 'is_correct': (i + 1 == self.correct_option)}
            for i, opt in enumerate(self.option_lines)
        ]
