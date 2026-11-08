from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class CMSHomePage(Page):
    intro = RichTextField(blank=True)
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    max_count = 1
    subpage_types = ["cms.CMSPage"]
    template = "cms/home_page.html"


class CMSPage(Page):
    intro = RichTextField(blank=True)
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    parent_page_types = ["cms.CMSHomePage", "cms.CMSPage"]
    subpage_types = ["cms.CMSPage"]
    template = "cms/cms_page.html"


class SiteSetting(models.Model):
    site_name = models.CharField(max_length=200, default="OlivePharma")
    tagline = models.CharField(max_length=300, blank=True)

    panels = [
        FieldPanel("site_name"),
        FieldPanel("tagline"),
    ]

    class Meta:
        verbose_name = "Site setting"

    def __str__(self):
        return self.site_name
