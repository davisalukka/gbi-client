# -:- encoding: utf-8 -:-
# This file is part of the GBI project.
# Copyright (C) 2012 Omniscale GmbH & Co. KG <http://omniscale.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import render_template, abort, flash, g, request, redirect, url_for, Blueprint
from flaskext.babel import _
from ...model.sources import LocalWMTSSource

from geobox.model import ExternalWMTSSource

from geobox.web.forms import RasterSourceForm, WMSForm, UnlockRasterSourceForm

raster = Blueprint('raster', __name__)


@raster.route('/admin/raster/list', methods=["GET"])
def raster_list():
    external_sources = g.db.query(ExternalWMTSSource).filter_by(is_user_defined=False).all()
    user_sources = g.db.query(ExternalWMTSSource).filter_by(is_user_defined=True).all()
    local_sources = g.db.query(LocalWMTSSource).all()
    return render_template('admin/external_raster_list.html', external_sources=external_sources, user_sources=user_sources, local_sources=local_sources)

@raster.route('/admin/wmts/unlock/<int:id>', methods=["GET", "POST"])
def raster_unlock(id):
    source = g.db.query(ExternalWMTSSource).filter_by(id=id).first()
    form = UnlockRasterSourceForm(request.form, source)
    if form.validate_on_submit():
        source.username = form.data['username']
        source.password = form.data['password']
        flash( _('update WMTS'), 'success')
        g.db.commit()
        return redirect(url_for('.raster_list'))

    return render_template('admin/external_unlock.html', source=source, form=form)

@raster.route('/admin/wms/edit', methods=["GET", "POST"])
@raster.route('/admin/wms/edit/<int:id>', methods=["GET", "POST"])
def wms_edit(id=None):
    wms = g.db.query(ExternalWMTSSource).filter_by(id=id).first() if id else None
    if wms and not wms.is_user_defined:
        abort(404)

    form = WMSForm(request.form, wms)
    if form.validate_on_submit():
        if not wms:
            wms = ExternalWMTSSource(
                name=form.data['name'],
                title=form.data['title'],
                url=form.data['url'],
                layer = form.data['layer'],
                format = form.data['format'],
                srs = form.data['srs'],
                username = form.data['username'],
                password = form.data['password'],
                is_user_defined=True,
                source_type='wms',
            )
            g.db.add(wms)
            flash( _('Save local WMS'), 'success')
        else:
            wms.name  = form.data['name']
            wms.title = form.data['title']
            wms.url = form.data['url']
            wms.layer = form.data['layer']
            wms.format = form.data['format']
            wms.version = form.data['version']
            wms.srs = form.data['srs']
            wms.username = form.data['username']
            wms.password = form.data['password']
            flash( _('update WMS'), 'success')
        g.db.commit()
        return redirect(url_for('.raster_list'))
    return render_template('admin/external_wms.html', form=form)

@raster.route('/admin/wmts/edit', methods=["GET", "POST"])
@raster.route('/admin/wmts/edit/<int:id>', methods=["GET", "POST"])
def wmts_edit(id=None):
    wmts = g.db.query(ExternalWMTSSource).filter_by(id=id).first() if id else None
    if wmts and not wmts.is_user_defined:
        abort(404)

    form = RasterSourceForm(request.form, wmts)

    if form.validate_on_submit():
        if not wmts:
            wmts = ExternalWMTSSource(
                name=form.data['name'],
                title=form.data['title'],
                url=form.data['url'],
                username = form.data['username'],
                password = form.data['password'],
                is_user_defined= True,
                source_type='wmts'
            )
            g.db.add(wmts)
            flash( _('Save local WMTS'), 'success')
        else:
            wmts.name  = form.data['name']
            wmts.title = form.data['title']
            wmts.url = form.data['url']
            wmts.username = form.data['username']
            wmts.password = form.data['password']
            flash( _('update WMTS'), 'success')
        g.db.commit()
        return redirect(url_for('.raster_list'))
    return render_template('admin/external_wmts.html', form=form)

@raster.route('/admin/raster/remove/<int:id>', methods=["GET", "POST"])
def raster_remove(id):
    raster_source = g.db.query(ExternalWMTSSource).with_polymorphic('*').filter_by(id=id).filter_by(is_user_defined=True).first()

    if not raster_source:
        abort(404)

    g.db.delete(raster_source)
    g.db.commit()
    flash( _('delete source successful'), 'success')
    return redirect(url_for('.raster_list'))