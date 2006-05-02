"""
5. Many-to-many relationships

To define a many-to-many relationship, use ManyToManyField().

In this example, an article can be published in multiple publications,
and a publication has multiple articles.
"""

from django.db import models

class Publication(models.Model):
    title = models.CharField(maxlength=30)

    def __repr__(self):
        return self.title

    class Meta:
        ordering = ('title',)

class Article(models.Model):
    headline = models.CharField(maxlength=100)
    publications = models.ManyToManyField(Publication)

    def __repr__(self):
        return self.headline

    class Meta:
        ordering = ('headline',)

API_TESTS = """
# Create a couple of Publications.
>>> p1 = Publication(id=None, title='The Python Journal')
>>> p1.save()
>>> p2 = Publication(id=None, title='Science News')
>>> p2.save()
>>> p3 = Publication(id=None, title='Science Weekly')
>>> p3.save()

# Create an Article.
>>> a1 = Article(id=None, headline='Django lets you build Web apps easily')
>>> a1.save()

# Associate the Article with a Publication.
>>> a1.publications.add(p1)

# Create another Article, and set it to appear in both Publications.
>>> a2 = Article(id=None, headline='NASA uses Python')
>>> a2.save()
>>> a2.publications.add(p1, p2)
>>> a2.publications.add(p3)

# Adding a second time is OK
>>> a2.publications.add(p3)

# Add a Publication directly via publications.add by using keyword arguments.
>>> new_publication = a2.publications.create(title='Highlights for Children')

# Article objects have access to their related Publication objects.
>>> a1.publications.all()
[The Python Journal]
>>> a2.publications.all()
[Highlights for Children, Science News, Science Weekly, The Python Journal]

# Publication objects have access to their related Article objects.
>>> p2.article_set.all()
[NASA uses Python]
>>> p1.article_set.all()
[Django lets you build Web apps easily, NASA uses Python]
>>> Publication.objects.get(id=4).article_set.all()
[NASA uses Python]

# We can perform kwarg queries across m2m relationships
>>> Article.objects.filter(publications__id__exact=1)
[Django lets you build Web apps easily, NASA uses Python]
>>> Article.objects.filter(publications__pk=1)
[Django lets you build Web apps easily, NASA uses Python]

>>> Article.objects.filter(publications__title__startswith="Science")
[NASA uses Python, NASA uses Python]

>>> Article.objects.filter(publications__title__startswith="Science").distinct()
[NASA uses Python]

# Reverse m2m queries are supported (i.e., starting at the table that doesn't
# have a ManyToManyField).
>>> Publication.objects.filter(id__exact=1)
[The Python Journal]
>>> Publication.objects.filter(pk=1)
[The Python Journal]

>>> Publication.objects.filter(article__headline__startswith="NASA")
[Highlights for Children, Science News, Science Weekly, The Python Journal]

>>> Publication.objects.filter(article__id__exact=1)
[The Python Journal]

>>> Publication.objects.filter(article__pk=1)
[The Python Journal]

# If we delete a Publication, its Articles won't be able to access it.
>>> p1.delete()
>>> Publication.objects.all()
[Highlights for Children, Science News, Science Weekly]
>>> a1 = Article.objects.get(pk=1)
>>> a1.publications.all()
[]

# If we delete an Article, its Publications won't be able to access it.
>>> a2.delete()
>>> Article.objects.all()
[Django lets you build Web apps easily]
>>> p1.article_set.all()
[Django lets you build Web apps easily]

# Adding via the 'other' end of an m2m
>>> a4 = Article(headline='NASA finds intelligent life on Earth')
>>> a4.save()
>>> p2.article_set.add(a4)
>>> p2.article_set.all()
[NASA finds intelligent life on Earth]
>>> a4.publications.all()
[Science News]

# Adding via the other end using keywords
>>> new_article = p2.article_set.create(headline='Oxygen-free diet works wonders')
>>> p2.article_set.all()
[NASA finds intelligent life on Earth, Oxygen-free diet works wonders]
>>> a5 = p2.article_set.all()[1]
>>> a5.publications.all()
[Science News]

# Removing publication from an article:
>>> a4.publications.remove(p2)
>>> p2.article_set.all()
[Oxygen-free diet works wonders]
>>> a4.publications.all()
[]

# And from the other end
>>> p2.article_set.remove(a5)
>>> p2.article_set.all()
[]
>>> a5.publications.all()
[]

# Relation sets can be assigned. Assignment clears any existing set members
>>> p2.article_set = [a4, a5]
>>> p2.article_set.all()
[NASA finds intelligent life on Earth, Oxygen-free diet works wonders]
>>> a4.publications.all()
[Science News]
>>> a4.publications = [p3]
>>> p2.article_set.all()
[Oxygen-free diet works wonders]
>>> a4.publications.all()
[Science Weekly]

# Relation sets can be cleared:
>>> p2.article_set.clear()
>>> p2.article_set.all()
[]
>>> a4.publications.all()
[Science Weekly]

# And you can clear from the other end
>>> p2.article_set.add(a4, a5)
>>> p2.article_set.all()
[NASA finds intelligent life on Earth, Oxygen-free diet works wonders]
>>> a4.publications.all()
[Science News, Science Weekly]
>>> a4.publications.clear()
>>> a4.publications.all()
[]
>>> p2.article_set.all()
[Oxygen-free diet works wonders]

# Recreate the article and Publication we just deleted.
>>> p1 = Publication(id=None, title='The Python Journal')
>>> p1.save()
>>> a2 = Article(id=None, headline='NASA uses Python')
>>> a2.save()
>>> a2.publications.add(p1, p2, p3)

# Bulk delete some Publications - references to deleted publications should go
>>> Publication.objects.filter(title__startswith='Science').delete()
>>> Publication.objects.all()
[Highlights for Children, The Python Journal]
>>> Article.objects.all()
[Django lets you build Web apps easily, NASA finds intelligent life on Earth, NASA uses Python, Oxygen-free diet works wonders]
>>> a2.publications.all()
[The Python Journal]

# Bulk delete some articles - references to deleted objects should go
>>> q = Article.objects.filter(headline__startswith='Django')
>>> print q
[Django lets you build Web apps easily]
>>> q.delete()

# After the delete, the QuerySet cache needs to be cleared, and the referenced objects should be gone
>>> print q
[]
>>> p1.article_set.all()
[NASA uses Python]

"""
