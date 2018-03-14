# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-16 17:18
from __future__ import absolute_import, division, print_function, unicode_literals

from django.db import migrations

from temba.contacts.search import BoolCombination, Condition


def rewrite_query_node(node):
    if isinstance(node, BoolCombination):
        ch_list = []

        for ch in node.children:
            if not (isinstance(ch, Condition)) or ch.prop not in ('name', 'id'):
                rw_q = rewrite_query_node(ch)
                if rw_q is not None:
                    ch_list.append(rw_q)
        if len(ch_list) == 0:
            return None
        node.children = ch_list
    elif isinstance(node, Condition) and node.prop in ('name', 'id'):
        return None

    return node


def rewrite_dynamic_contactgroups(dynamic_groups_qs):
    """
    Rewrites queries for dynamic contact groups

    * normalizes a query as parsed_query.as_text() -> converts implicit to explicit query
    * rewrite normalized query to remove all nodes with property 'name'
    * saves the rewritten query to the database
      * if the query is None, that will effectively dedynamicify the ContactGroup
    """
    from ..search import parse_query

    groups = dynamic_groups_qs.select_related('org')
    if not groups:
        return

    print("Found %d dynamic groups to migrate..." % len(groups))

    for dg in groups:
        try:
            parsed_query = parse_query(dg.query, as_anon=dg.org.is_anon)

            new_root_node = rewrite_query_node(parsed_query.root)
            if new_root_node is not None:
                parsed_query.root = new_root_node

                new_query = parsed_query.as_text()
            else:
                new_query = None
        except ValueError:
            new_query = None

        print(" > Migrated group '%s' #%d ('%s' => '%s')" % (dg.name, dg.id, dg.query, new_query))

        dg.query = new_query
        dg.save(update_fields=('query',))


def apply_manual():
    from temba.contacts.models import ContactGroup
    rewrite_dynamic_contactgroups(ContactGroup.user_groups.exclude(query__isnull=True))


def apply_as_migration(apps, schema_editor):
    ContactGroup = apps.get_model('contacts', 'ContactGroup')
    dg_qs = ContactGroup.all_groups.exclude(query__isnull=True).filter(group_type='U', is_active=True)
    rewrite_dynamic_contactgroups(dg_qs)


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0067_auto_20170808_1852'),
    ]

    operations = [
        migrations.RunPython(apply_as_migration)
    ]