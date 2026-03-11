from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):

    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return [
            "index",
            "privacy",
            "offer",
            "terms",
        ]

    def location(self, item):
        return reverse(item)
