/*

Script: Sickbeard.js

    The client-side javascript code for the Deluge Sickbeard plugin.

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

*/


///////////////////////////////////////////////////////////////////////////////
// Helper functions
///////////////////////////////////////////////////////////////////////////////

function bytesToSize(bytes) {
   var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
   if (bytes == 0) return '0 Byte';
   var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
   return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
};

function humanTime(cum_time) {
    if (cum_time == -1 || null == cum_time) {
        value = _('N/A');
    } else if ( cum_time < 60 ) {
        value = cum_time.toFixed(0) + ' ' + _('sec');
    } else if ( cum_time < 60 * 60) {
        value = cum_time / 60;
        value = value.toFixed(0) + ' ' + _('min');
    } else {
        value = cum_time / ( 60 * 60 );
        value = value.toFixed(1) +  ' ' + _('hours');
    }

    return value;
}

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
}

function formatLogRecord(record, patterns) {

    success = patterns.success;
    error   = patterns.error;

    success.push("post-process status success");

    msg = record.msg;

    err = error.some(function(regex){
        re = new RegExp(regex);
        return re.test(msg);
    });

    if (err || record.levelname == 'ERROR') {
        msg = '<span style=\'color: red;\'>' + msg + '</span>';
    } else {
        suc = success.some(function(regex){
            re = new RegExp(regex);
            return re.test(msg);
        });

        if (suc) {
            msg = '<span style=\'color: green;\'>' + msg + '</span>';
        }
    }

    return record.asctime.replace(/.* /, '') + " " +
           record.levelname + " " +
           //record.name.replace('deluge.sickbeard.', '') + " " +
           msg
}

///////////////////////////////////////////////////////////////////////////////
// ExtJS extensions
///////////////////////////////////////////////////////////////////////////////

Ext.override(Ext.form.Field,
    {   afterRender : Ext.form.Field.prototype.afterRender.createSequence(function()
        {
            var qt = this.qtip;
            if (qt)
            {   Ext.QuickTips.register({
                target:  this,
                title: '',
                text: qt,
                enabled: true,
                showDelay: 10,
                dismissDelay: 10000
                });
            }
        })
});

// ExtJS Data Proxy to retrieve data using Ext.ux.util.RpcClient
// (deluge.client). This allows use of the ExtJS stores without
// the need for manually filling ExtJS stores.
//
Ext.data.DelugeProxy = function() {
    var api = {};

    api[Ext.data.Api.actions.read] = true;

    Ext.data.DelugeProxy.superclass.constructor.call(this, {
        api: api
    });
};

Ext.extend(Ext.data.DelugeProxy, Ext.data.DataProxy, {
    doRequest : function(action, rs, params, reader, callback, scope, arg) {
        // No implementation for CRUD. Assumes all actions are 'load'

        params = params || {};

        deluge.client.sickbeard.get_post_process_methods({
            scope: this,
            success: function(data) {
                var records;
                try {
                    records = reader.readRecords(data);
                }catch(e){
                    // @deprecated loadexception
                    this.fireEvent("loadexception", this, null, arg, e);
                    this.fireEvent('exception', this, 'response', action, arg, null, e);

                    callback.call(scope, null, arg, false);
                    return;
                }

                callback.call(scope, records, arg, true);
            },

            falure: function(e) {

                //
                // Todo: verify if e can be used in fireEvent
                //

                // @deprecated loadexception
                this.fireEvent("loadexception", this, null, arg, e);
                this.fireEvent('exception', this, 'response', action, arg, null, e);

                callback.call(scope, null, arg, false);
            }
        });
    }
});



///////////////////////////////////////////////////////////////////////////////
// Preference page
///////////////////////////////////////////////////////////////////////////////

Ext.ns('Deluge.ux.preferences');

Deluge.ux.preferences.SickbeardPage = Ext.extend(Ext.form.FormPanel, {

    title: _('Sickbeard'),
    layout: 'fit',
    border: false,

    initComponent: function() {

        Deluge.ux.preferences.SickbeardPage.superclass.initComponent.call(this);

        // Tab Settings
        ///////////////

        this.fsetInfo = new Ext.form.FieldSet({
            border: false,
            title: '',
            style: 'margin-bottom: 0px; padding-bottom: 5px; padding-top: 5px;',
            labelWidth: '100%',
            autoHeight: true,
        });

        this.fsetInfo.add({
            xtype: 'panel',
            border: false,
            width: '100%',
            style: 'margin-bottom: 10px',
            bodyCfg: {
                html: _('Provide connection and authentication details of the Sickbeard instance '
                    +   'Deluge will connect to for post-processing.<br /><br /><i>Note that at this moment a '
                    +   'specific version of Sickbeard is required to fully make use of the post-'
                    +   'processing options of this plugin. The name of the fork is '
                    +   '<a href="https://github.com/srluge/SickRage" target="_blank">"srluge/SickRage"</a>. The plan is '
                    +   'to request a merge of this fork with Sickrage main.</i>')
            }
        });

        this.fsetConn = new Ext.form.FieldSet({
            border: false,
            title: _('Connection'),
            style: 'margin-bottom: 0px; padding-bottom: 5px; padding-top: 5px;',
            labelWidth: 110,
            autoHeight: true,
            defaultType: 'textfield',
            defaults: {
                width: 180,
            }
        });

        this.fsetConn.add({
            name: 'host',
            fieldLabel: _('Hostname'),
            qtip: _('Specify name of the host where Sickbeard is running. Default is localhost.')
        });

        this.fsetConn.add({
            xtype: 'spinnerfield',
            name: 'port',
            fieldLabel: _('Port'),
            margins: '2 0 0 34',
            width: 64,
            decimalPrecision: 0,
            minValue: 0,
            maxValue: 65535,
            qtip: _('Specify port number on the host where Sickbeard is running. Default is 8081.')
        });

        this.chkSSL = this.fsetConn.add({
            xtype: 'checkbox',
            name: 'ssl',
            hideLabel: true,
            width: 280,
            boxLabel: _('Use SSL'),
            qtip: _('Specify if the connection uses SSL (HTTPS). Default is not to use SSL.')
        });

        this.fsetAuth =  new Ext.form.FieldSet({
            xtype: 'fieldset',
            border: false,
            title: _('Authentication'),
            style: 'margin-bottom: 0px; padding-bottom: 5px; padding-top: 5px;',
            labelWidth: 110,
            autoHeight: true,
            defaultType: 'textfield',
            defaults: {
                width: 180,
            }
        });

        this.fsetAuth.add({
            name: 'username',
            fieldLabel: _('Username'),
            qtip: _('Provide the username configured in Sickbeard. Default is not to use a name.')
        });

        this.fsetAuth.add({
            name: 'password',
            fieldLabel: _('Password'),
            inputType: 'password',
            qtip: _('Provide the password configured in Sickbeard. Default is not to use a password.')
        });

        this.fsetTest = new Ext.form.FieldSet({
            xtype: 'fieldset',
            border: false,
            title: _('Connection Test'),
            style: 'margin-bottom: 0px; padding-bottom: 5px; padding-top: 5px;',
            labelWidth: 110,
            autoHeight: true,
            defaultType: 'textfield',
            defaults: {
                width: 180,
            },
            layout: 'column',
            columnWidth: 0.5
        });

        this.btnTest = this.fsetTest.add({
            xtype: 'button',
            text: _('Test connection'),
            listeners: {
                'click': {
                    fn: this.onTestConnection,
                    scope: this
                }
            },
            columnWidth: 0.5
        });

        this.lblStatus = this.fsetTest.add({
            xtype: 'label',
            text: _('Connection: N/A'),
            disabled: true,
            hideLabel: true,
            columnWidth: 0.5,
            style: 'margin-left: 15px; margin-top: 4px;'
        });


        // Tab Processing
        /////////////////

        this.fsetProcInfo = new Ext.form.FieldSet({
            border: false,
            title: '',
            style: 'margin-bottom: 0px; padding-bottom: 5px; padding-top: 5px;',
            labelWidth: '100%',
            autoHeight: true,
        });

        this.fsetProcInfo.add({
            xtype: 'panel',
            border: false,
            width: '100%',
            style: 'margin-bottom: 10px',
            bodyCfg: {
                html: _('Specify the Sickbeard post-processing method and '
                    +   'configure how this plugin should handle post-processed '
                    +   'torrents.')
            }
        });

        this.fsetProcSickbeard = new Ext.form.FieldSet({
            border: false,
            title: _('Sickbeard'),
            style: 'margin-bottom: 0px; padding-bottom: 5px; padding-top: 5px;',
            labelWidth: 110,
            autoHeight: true,
            defaultType: 'textfield',
            defaults: {
                width: 180,
            }
        });

        // Cannot auto load store. deluge.client.sickbeard.* is not ready during
        // plugin initialization.
        //
        this.storeMethods = new Ext.data.JsonStore({
            // store config
            autoDestroy: true,
            storeId: 'methods',

            // reader config
            root: 'methods',
            idProperty: 'method',
            fields: ['method', 'translation' ],

            proxy: new Ext.data.DelugeProxy()
        });

        this.cmbMethod = this.fsetProcSickbeard.add({
            xtype: 'combo',
            fieldLabel: _('Post-processing method'),
            store: this.storeMethods,
            // Though store is 'remote', we load store manually. To prevent loading
            // a second time when clicking the combo box, method must be set to
            // mode to local.
            mode: 'local',
            valueField: 'method',
            displayField: 'translation',
            hiddenName: 'method',
            editable: false,
            forceSelection: true,
            triggerAction: 'all',
            qtip: _("Specify Sickbeard post-processing method. 'Sickbeard Default' selects the default method " +
                    "configured in Sickbeard. To override the Sickbeard default, use one of the other options.")
        });

        this.fsetProcPlugin = new Ext.form.FieldSet({
            border: false,
            title: _('Plugin'),
            style: 'margin-bottom: 0px; padding-bottom: 5px; padding-top: 5px;',
            labelWidth: 110,
            autoHeight: true,
            defaultType: 'textfield',
            defaults: {
                width: 180,
            }
        });

        this.fsetProcPlugin.add({
            xtype: 'spinnerfield',
            name: 'workers',
            fieldLabel: _('Workers (requires Deluge restart)'),
            margins: '2 0 0 34',
            width: 64,
            decimalPrecision: 0,
            minValue: 1,
            maxValue: 20,
            qtip: _("Specify the maximum number of 'workers' that in parallel may send post-processing tasks to " +
                    "Sickbeard. When bulk post-processing torrents, this prevents that both Sickbeard as well as " +
                    "Deluge get congested with post-processing tasks. Required restart of Deluge.")
        });

        this.chkRemove = this.fsetProcPlugin.add({
            xtype: 'checkbox',
            name: 'remove',
            hideLabel: true,
            width: 280,
            boxLabel: _('Remove torrent after successfully post-processed'),
            listeners: {
                scope: this,
                check: function(cb, checked) {
                    this.chkRemoveData.setDisabled(!checked);
                }
            },
            qtip: _("Specify whether a torrent should be removed afther Sickbeard was able to successfully " +
                    "post-process it. Note that torrents marked as 'failed' will also be removed, if " +
                    "Sickbeard was successfully abto to register the torrent-release as 'failed download'.")
        });

        this.chkRemoveData = this.fsetProcPlugin.add({
            xtype: 'checkbox',
            name: 'remove_data',
            hideLabel: true,
            width: 280,
            disabled: true,
            boxLabel: _('Also remove torrent data'),
            qtip: _("Also remove torrent data.")
        });


        // Tab Failed download handling
        ///////////////////////////////

        this.fsetFailedInfo = new Ext.form.FieldSet({
            border: false,
            title: '',
            style: 'margin-bottom: 0px; padding-bottom: 5px; padding-top: 5px;',
            labelWidth: '100%',
            autoHeight: true,
        });

        this.fsetFailedInfo.add({
            xtype: 'panel',
            border: false,
            width: '100%',
            style: 'margin-bottom: 10px',
            bodyCfg: {
                html: _("Automatically detect a failed torrent and post-process " +
                        "the failed download with Sickbeard. This requires a "    +
                        "Sickbeard fork with failed download detection included." )
            }
        });

        this.fsetFailed = new Ext.form.FieldSet({
            border: false,
            title: _('Automatic failed processing'),
            style: 'margin-bottom: 0px; padding-bottom: 5px; padding-top: 5px;',
            labelWidth: 110,
            autoHeight: true,
            defaultType: 'textfield',
            defaults: {
                width: 180,
            }
        });

        this.fsetFailed.add({
            xtype: 'checkbox',
            name: 'failed',
            hideLabel: true,
            width: 280,
            boxLabel: _('Enabled'),
            listeners: {
                scope: this,
                check: function(cb, checked) {
                    this.chkFailedInterval.setDisabled(!checked);
                    this.chkFailedLimit.setDisabled(!checked);
                    this.chkFailedTime.setDisabled(!checked);
                    this.chkFailedLabel.setDisabled(!checked);
                    this.txtFailedLabelName.setDisabled(!checked);
                }
            },
            qtip: _("Enable or disabled automatic failed download post-processing.")
        });

        this.chkFailedLabel = this.fsetFailed.add({
            xtype: 'checkbox',
            name: 'failed_label',
            hideLabel: true,
            width: 280,
            boxLabel: _('Process only torrents with label'),
            listeners: {
                scope: this,
                check: function(cb, checked) {
                    this.txtFailedLabelName.setDisabled(!checked);
                }
            },
            qtip: _("Only perform failure detection on torrents with a specific label. Otherwise perform failure detection on all torrents. Default is enabeld.")
        });

        this.txtFailedLabelName = this.fsetFailed.add({
            name: 'failed_label_name',
            fieldLabel: _('Label name'),
            qtip: _('Specify the label name which will need to be set on the torrent. Default is sickbeard.')
        });

        this.fsetFailedAvail = new Ext.form.FieldSet({
            border: false,
            title: _('Availability based (Soft limit)'),
            style: 'margin-bottom: 0px; padding-bottom: 5px; padding-top: 5px;',
            labelWidth: 110,
            autoHeight: true,
            defaultType: 'textfield',
            defaults: {
                width: 180,
            }
        });

        this.chkFailedLimit = this.fsetFailedAvail.add({
            xtype: 'spinnerfield',
            name: 'failed_limit',
            fieldLabel: _('When unavailable longer then(hours)'),
            margins: '2 0 0 34',
            width: 64,
            decimalPrecision: 0,
            minValue: 1,
            disabled: true,
            qtip: _("...")
        });

        this.fsetFailedTime = new Ext.form.FieldSet({
            border: false,
            title: _('Time based (Hard limit)'),
            style: 'margin-bottom: 0px; padding-bottom: 5px; padding-top: 5px;',
            labelWidth: 110,
            autoHeight: true,
            defaultType: 'textfield',
            defaults: {
                width: 180,
            }
        });

        this.chkFailedTime = this.fsetFailedTime.add({
            xtype: 'spinnerfield',
            name: 'failed_time',
            fieldLabel: _('When downloading longer then(hours)'),
            margins: '2 0 0 34',
            width: 64,
            decimalPrecision: 0,
            minValue: 1,
            disabled: true,
            qtip: _("...")
        });

        this.fsetFailedAdvanced = new Ext.form.FieldSet({
            border: false,
            title: _('Advanced'),
            style: 'margin-bottom: 0px; padding-bottom: 5px; padding-top: 5px;',
            labelWidth: 110,
            autoHeight: true,
            defaultType: 'textfield',
            defaults: {
                width: 180,
            }
        });

        this.chkFailedInterval = this.fsetFailedAdvanced.add({
            xtype: 'spinnerfield',
            name: 'failed_interval',
            fieldLabel: _('Check interval(seconds)'),
            margins: '2 0 0 34',
            width: 64,
            decimalPrecision: 0,
            minValue: 1,
            disabled: true,
            qtip: _("...")
        });

        this.tabPanSettings = this.add({
            xtype: 'tabpanel',
            activeTab: 0,
            items: [{
                    title: _('Settings'),
                    layout: 'form',
                    items: [this.fsetInfo, this.fsetConn, this.fsetAuth, this.fsetTest],
                    autoScroll: true
                },{
                    title: _('Processing'),
                    layout: 'form',
                    items: [this.fsetProcInfo, this.fsetProcSickbeard, this.fsetProcPlugin]
                },{
                    title: _('Failed'),
                    layout: 'form',
                    items: [this.fsetFailedInfo, this.fsetFailed, this.fsetFailedAvail, this.fsetFailedTime, this.fsetFailedAdvanced]
                }
            ]
        });

        this.on('show', this.updateConfig, this);
    },

    updateConfig: function() {
        this.lblStatus.setText(('Connection: N/A'));_

        this.storeMethods.load();

        // We should display/enable form only after *all* async remote
        // calls have been completed. But for now being lazy...
        //
        deluge.client.sickbeard.get_config({
            scope: this,
            success: function(config) {
                this.config = config;
                this.getForm().setValues(config);
            }
        });
    },

    onApply: function() {
        this.mergeConfig();
        deluge.client.sickbeard.set_config(this.config);
    },

    onOk: function() {
        this.onApply();
    },

    onDestroy: function() {
        deluge.preferences.un('show', this.updateConfig, this);
        Deluge.ux.preferences.SickbeardPage.superclass.onDestroy.call(this);
    },

    onTestConnection: function() {
        this.lblStatus.setText('Connection: connecting...');
        this.btnTest.setDisabled(true);
        try {
            deluge.client.sickbeard.test_connection(this.config, {
                scope: this,
                success: function(response) {
                    if (response.success) {
                        this.lblStatus.setText('Connection: succeeded');
                    } else{
                        this.lblStatus.setText(response.data);
                    }
                    this.btnTest.setDisabled(false);
                },
                failure: function(reason) {
                    this.lblStatus.setText(reason.error.msg);
                    this.btnTest.setDisabled(false);
                }
            });
        } catch (err) {
            this.btnTest.setDisabled(false);
            this.lblStatus.setText('Connection: failed');
        }
    },

    mergeConfig: function() {
        var config = this.getForm().getValues();

        // Don't use 'on' as a values for checkboxes but
        // actual true/false boolen value
        this.getForm().items.each(function(item) {
            if (item.xtype == 'checkbox') {
                config[item.name] = item.getValue();
            }
        });

        // Merge form values with cached config object
        for (var key in this.config) {
            if (key in config) {
                this.config[key] = config[key]
            }
        }
    }
});



///////////////////////////////////////////////////////////////////////////////
// Deluge UI
///////////////////////////////////////////////////////////////////////////////

Ext.ns('Deluge.ux.Sickbeard');

Deluge.ux.Sickbeard.ShowLog = Ext.extend(Ext.Window, {

        title: _('Sickbeard post-processing log'),
        width: 800,
        height: 550,
        iconCls: 'sickbeard-log-icon16',
        layout: {
            type: 'vbox',
            align : 'stretch',
            pack  : 'start',
        },
        closeAction: 'hide',

        initComponent: function() {

            Deluge.ux.Sickbeard.ShowLog.superclass.initComponent.call(this);

            this.overview = this.add({
                id: 'overview',
                title: 'Task overview',
                margins: ' 10 5 5 5',
                cmargins: ' 10 5 5 5',
                layout: 'column',
                border: false
            });

            this.form_left = this.overview.add({
                xtype: 'form',
                id: 'form-left',
                columnWidth: .50,
                bodyStyle: 'padding:15px',
                width: 350,
                defaultType: 'displayfield',
                border: false,
                defaults: {
                    width: 230,
                    bodyStyle: 'padding: 2px',
                    labelStyle: 'font-weight:bold;'
                },
                items: [{
                        fieldLabel: 'Task Id',
                        id: 'task_id',
                    },{
                        fieldLabel: 'Torrent Name',
                        id: 'torrent_name'
                    },{
                        fieldLabel: 'Torrent ID',
                        id: 'torrent_id'
                    },{
                        fieldLabel: 'Magnet',
                        id: 'magnet'
                    },{
                        fieldLabel: 'Sickbeard status',
                        id: 'status'
                    }
                ],
                layoutConfig: {
                    labelSeparator: ':' // superseded by assignment below
                },
                hideLabels: false,
                labelAlign: 'left'
            });

            this.form_right = this.overview.add({
                xtype: 'form',
                id: 'form-right',
                columnWidth: .50,
                bodyStyle: 'padding:15px',
                width: 350,
                defaultType: 'displayfield',
                border: false,
                defaults: {
                    // applied to each contained item
                    width: 230,
                    bodyStyle: 'padding: 2px',
                    msgTarget: 'side',
                    labelStyle: 'font-weight:bold;'
                },
                items: [{
                        fieldLabel: 'Start time',
                        id: 'start_time',
                    },{
                        fieldLabel: 'End time',
                        id: 'end_time'
                    },{
                        fieldLabel: 'Saved path',
                        id: 'save_path'
                    },{
                        fieldLabel: 'Download completed',
                        id: 'completed'
                    },{
                        fieldLabel: 'Size',
                        id: 'size'
                    }
                ],
                layoutConfig: {
                    labelSeparator: ':'
                },
                hideLabels: false,
                labelAlign: 'left'
            });

            this.output = this.add( [
                {
                    id: 'output',
                    title: 'Sickbeard post-processing output',
                    html: '',
                    flex: 1,
                    margins: ' 5 5 5 5',
                    cmargins: ' 5 5 5 5',
                    autoScroll: true
                },
            ]);

            this.addButton(_('Ok'), this.onOkClick, this);
        },

        onOkClick: function() {
            this.hide();
        }
});

Deluge.ux.Sickbeard.PostProcessDialog = Ext.extend(Ext.Window, {

        title: _('Post-process item(s) with Sickbeard'),
        width: 800,
        height: 550,
        iconCls: 'sickbeard-icon16',
        layout: {
            type: 'vbox',
            align : 'stretch',
            pack  : 'start',
        },
        closeAction: 'hide',

        initComponent: function() {

            Deluge.ux.Sickbeard.ShowLog.superclass.initComponent.call(this);

            this.overview = this.add({
                id: 'overview',
                title: 'Task overview',
                margins: ' 10 5 5 5',
                cmargins: ' 10 5 5 5',
                layout: 'column',
                border: false
            });

            this.form_left = this.overview.add({
                xtype: 'form',
                id: 'form-left',
                columnWidth: .50,
                bodyStyle: 'padding:15px',
                width: 350,
                defaultType: 'displayfield',
                border: false,
                defaults: {
                    width: 230,
                    bodyStyle: 'padding: 2px',
                    labelStyle: 'font-weight:bold;'
                },
                items: [{
                        fieldLabel: 'Task Id',
                        value: 'hellooh',
                        id: 'task_id',
                    },{
                        fieldLabel: 'Torrent Name',
                        id: 'torrent_name'
                    },{
                        fieldLabel: 'Torrent ID',
                        id: 'torrent_id'
                    },{
                        fieldLabel: 'Magnet',
                        id: 'magnet'
                    },{
                        fieldLabel: 'Sickbeard status',
                        id: 'status'
                    }
                ],
                layoutConfig: {
                    labelSeparator: ':' // superseded by assignment below
                },
                hideLabels: false,
                labelAlign: 'left'
            });

            this.form_right = this.overview.add({
                xtype: 'form',
                id: 'form-right',
                columnWidth: .50,
                bodyStyle: 'padding:15px',
                width: 350,
                defaultType: 'displayfield',
                border: false,
                defaults: {
                    // applied to each contained item
                    width: 230,
                    bodyStyle: 'padding: 2px',
                    msgTarget: 'side',
                    labelStyle: 'font-weight:bold;'
                },
                items: [{
                        fieldLabel: 'Start time',
                        id: 'start_time',
                    },{
                        fieldLabel: 'End time',
                        id: 'end_time'
                    },{
                        fieldLabel: 'Saved path',
                        id: 'save_path'
                    },{
                        fieldLabel: 'Download completed',
                        id: 'completed'
                    },{
                        fieldLabel: 'Size',
                        id: 'size'
                    }
                ],
                layoutConfig: {
                    labelSeparator: ':'
                },
                hideLabels: false,
                labelAlign: 'left'
            });

            this.output = this.add( [
                {
                    id: 'output',
                    title: 'Sickbeard post-processing output',
                    html: '',
                    flex: 1,
                    margins: ' 5 5 5 5',
                    cmargins: ' 5 5 5 5',
                    autoScroll: true
                },
            ]);

            this.addButton(_('Ok'), this.onOkClick, this);
        },

        onOkClick: function() {
            this.hide();
        }
});


///////////////////////////////////////////////////////////////////////////////
// Plugin
///////////////////////////////////////////////////////////////////////////////

Deluge.plugins.SickbeardPlugin = Ext.extend(Deluge.Plugin, {

    name: "Sickbeard",

    // Plugin is initialized when the Deluge web application is loaded in the
    // browser, or when plugin is enabled by the user via plugin preferences.
    // Plugin is only intialized *once* during an application session.
    // Subsequent enabling or disabling actions of the plugin via plugin
    // preferences will *not* re-initialize the plugin. Note that the Deluge
    // web application is fully reloaded when the browser is refreshed. The
    // plugin is then also initialized, if previously enabled.
    //
	constructor: function(config) {

        console.log('Sickbeard plugin initializing');

		Deluge.plugins.SickbeardPlugin.superclass.constructor.call(this, config);

        // CCS Image maps
        //
        this.icon16     = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3gYOCgMTKXvCpwAAA2ZJREFUOMtlkm1MVQUcxn/nnnPvwYtw74aEwgYY4i4gL0oxqEWaAiVJZR9kJMuSMUeQuLRmW1l+sJpbi3JWgmnowKSsUZsKcykTFE0xVKgVFwq5vF+4L9wL595zTh9shvZ8e7bnefbb/n+BB3T0jUzajl8Lf+Xg/q963Z608JAQiwHBP3fp2ObST3suPpgX5pvaqmSh/5ee6KzqjwbebD0lub1uRIMBVQvw3oZXWXD564KXP+ttmd8R55vowfGIgr377a/9dELOSRIoXhNKTkoIfkWk8fJVnskvK11vuXWmucsz9D+C7999aqMrqeC7vS1N5KYaqNoYihLQATBKAtsPuLAP+9mZX0LK+M2yp3edPAwg1lXaWB07naU8vrX1rR+OkLcqhLLCUHT9PzJNgxVLJZwugROXrpGUvraoQG4/9+LqZX8LAG2Hd3SWX+nMio+c48PycLw+HUnivhFJvEvy7G4niyOj+Dh5+fHc8gOlBoDJoJbldE0SZhZQNWj82UfXH4H7ym3dCqoKFc+Z6RsawGiNTgSQAEwCaLpOdrKJuYDOlgIzmn4XHSCoQm6aCSWo86jNBIhoyoxwb0DyOUdjImOimi5MsyZDxjWj0XJ1DtkkYF0oYHeoZCwzkp5g5OR5H6lLl+MdHxi5d8Yn49yrxKR1qTf6+rjVH8Dt0+noUYhfLOKd1RlxatS3+jEZoemCn7SEVOLGbp/+tv3OWbGuykZgZjreHZuZ//vQnww7A3TbgyyyGLA7VCbdGiZJYHBMpbsviCQKDE86KM4pzE5Uzn8gNl+ZYHt1ZcPn1zusHp+b3Zt24ZhyMDDsxO3TmXTrDE2oqGoAS2gYqhpk/SP5eGQL4cNdU+InJWF5cvZLVeawCCzmMHJklcKHbVjjVqJrKnNBhYSYRPYV72RlrA2Hy8no1BibM3MZ+fV0vcFktiQv8Y3ywmNFTPs8RMgyt8/UnEu/087b+Zv4pux9Kh5ayG+HSqdnPBPkZa6l5InnUeydSEY5Tqh7PTk0qMw2WhfFbpjK3kKKd5Dc4neE2kpbhkE0nlUDfgcI+3yuUX96RcOP3otHWBCzAntHQ7WO4aCkBoMz276wF9VWyeuE5j3HekXj+L//c2Nrzc0ogKM7UsG6JO6vU3sUZdZbr9mvS9u+7K8B+AdRwHNBWdS07QAAAABJRU5ErkJggg==';
        this.icon128    = 'data:image/png;base64,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';
        this.log_icon16 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAACkElEQVR42n2T2U8TURTGv5lpbSmlqbYEJNSiPvFkTFjUqDGCmBAVRGmpFX0xiInLszGGxJj4aIzGjb64YGmhUBbf/AMYbGJEEoMPQFg0LiQmlq7TGc+9sk1DPJlk7j0353e/c849Atat0mazdRSQrTpUVYOSyyGdTiOxHH9MrgnkmbDyt/r9/ukHDx8VM5fGgnMqEqk0vv1YwtzX73g3FPwVCATq6ejjZoDqvv7IeFXtfh1dVVUkUxn8/rOM3a5S3L51k0HqNipZBdT0RwbkfQcOIjoYgWuHG8lEAoqSQyabwd6qWjjsNg68e6drKdDdfYxiPuQBIvKhw0cQi8UgiiIFK5AkCYWFhSgnIGUESaT0NA03rl9bejs8uIfiFtcAlIJ8tK4eiwsLyCpZDmFFNJlMoChel+VkCpq4BeG+fty/11VLrnEdoKHhOCYnP/GqC4IAo9GITCYDg8HAFRUUWOCq2IlodAhXOy/pAUSVGxsbMTMzwzNTSAWDsLxXAXa7HQ6nE8PDI2j3+/SAEAFOnTyBqakvFAhkswo/YKkwgCSJKCkphcVi4YA2b2seINwnNzc3YWKCOqSxT4PRYOQ3C1Q85rNvtaNsexlGRkfh9eQBekNh+UxLC+bn5/jtrANcAd3MKs+U5AjmdlcgMjBACjx6QLA3JHtaz2JsbOzfAxFEOJ0OSCTfQDAGKS938fRYF3xtXj2gJ9gr+7weLFAbVda2leIxJSwN9qgcjm0oKipCMBSG39emA1S/eNUzfuH8OczOzvLAHA0Ru9XtdvNubLSXr9/gYru/hpbv14apqfn09JOnz4rNZhP+ZykasCudl38ORQd30Ta+EV1ptVo7zOb1cd4ckEzG4/HntPzM9n8B7MUhIOXcgRgAAAAASUVORK5CYII=';

        Ext.util.CSS.createStyleSheet('a img.sickbeard-log-icon {background-image: url(' + this.log_icon16 + '); background-repeat: no-repeat; height: 16px; width: 16px; padding: 0px; margin-left: 3px; vertical-align: middle; border: solid none; display: inline-block;}');
        Ext.util.CSS.createStyleSheet('.sickbeard-log-icon16 {background-image: url(' + this.log_icon16 + '); }');
        Ext.util.CSS.createStyleSheet('.sickbeard-icon16 {background-image: url(' + this.icon16 + '); }');

        // Toolbar button
        //
        this.toolbarBtn = new Ext.Button( { text: 'Sickbeard',
                                            id: 'sickbeard',
                                            cls: 'x-btn-text-icon',
                                            icon: this.icon16,
                                            scope: this,
                                            disabled: true,
                                            hidden: true,
                                            handler: this.showLog } );

        // Add Sickbeard's toolbar button right from connection manager button
        //
        var itemIndex = deluge.toolbar.items.findIndex('id', 'connectionman');

        if ( itemIndex != -1 ) {
            deluge.toolbar.insert( itemIndex + 1, this.toolbarBtn );
        } else {
            deluge.toolbar.add( this.toolbarBtn );
        }

        // Dialogs
        //
        this.dialogShowLog = false;

        // Torrent menu
        //
        this.torrentMenu = new Ext.menu.Menu();

        this.torrentMenu.s

        this.tmSep = deluge.menus.torrent.add({
            xtype: 'menuseparator'
        });

        this.tm = deluge.menus.torrent.add({
            text: _('Sickbeard'),
            menu: this.torrentMenu,
            icon: this.icon16,
            handler: this.process,
            scope: this
        });

        this.torrentMenu.addMenuItem({
            text: _('Process as success'),
            label: '',
            icon: this.icon16,
            handler: this.process_success,
            scope: this
        });

        this.torrentMenu.addMenuItem({
            text: _('Process as failed'),
            label: '',
            icon: this.icon16,
            handler: this.process_failed,
            scope: this
        });

        this.loggedin  = false;
        this.connected = false;
        this.enabled   = false;

        deluge.events.on('login'     , this.onLogin     , this);
        deluge.events.on('logout'    , this.onLogout    , this);
        deluge.events.on('connect'   , this.onConnect   , this);
        deluge.events.on('disconnect', this.onDisconnect, this);

        //deluge.events.on('SickbeardProcessCompletedEvent', this.processCompletedEvent, this);

        // *Hack* detect current logged in and connected statusses
        //
        btnLogout = deluge.toolbar.items.get('logout');
        loggedin  = (btnLogout) ? ! btnLogout.disabled : false;
        connected = deluge.ui.running;

        if (loggedin) {
            // Run onLogin code if plugin is initialized *after* login. This is the
            // case when manually enabling or disabling the plugin via preferences
            // window.
            //
            this.onLogin();

            if(connected) {
                // Run onConnect code if plugin is initialized *after* a connect
                // to a core. This is the case when manually enabling or disabling
                // the plugin via preferences window.
                //
                this.onConnect();
            }
        }

        // Once connected, the post-process output-patterns will be requested from
        // the server.
        //
        this.patterns_cache = { 'success': [], 'error': [] }
	},

	onEnable: function() {

        console.log('Sickbeard plugin enabled');

        this.enabled = true;

        // Immideately show the Sickbeard toolbar button. Button is disabled,
        // until actually connected to a Deluge core.
        //
        //this.toolbarBtn.show();
        //deluge.toolbar.doLayout();

        // And enable the button if previously connected to a deluge core.
        //
        if (this.connected) {
            this.toolbarBtn.enable();
        }

        // Register custom columns in torrents grid
        //
        this.registerTorrentStatus('sickbeard_download_status'  , _('Download Status')  , { colCfg:
            {
                sortable: true,
                tooltip: _('Download Status'),
                renderer: function(value, metadata) {
                    if (!value) {
                        value = _('N/A');
                    }
                    metadata.attr = 'ext:qtip="Torrent download status is  ' + value + '"';
                    return value;
                }
            }
        });
        this.registerTorrentStatus('sickbeard_processing_status', _('Processing Status'), { colCfg:
            {
                sortable: true,
                renderer: function(values, metadata) {
                    if (!values)
                        { return _('N/A'); }

                    values      = values.split('_');

                    var status  = values[0];
                    var task_id = values[1];

                    metadata.attr = 'ext:qtip="Post-processing status is  ' + status + '"';

                    if (status != 'none') {
                        return status +
                               '<a class="sickbeard-no-border" href="javascript:deluge.plugins.Sickbeard.showDetails(\'' + task_id + '\')">' +
                               '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNiYAAAAAkAAxkR2eQAAAAASUVORK5CYII=" src="javascript:" class="sickbeard-log-icon"/>' +
                               '</a>';
                    } else {
                        return 'none'
                    }
                },
                tooltip: _('Processing status')
            }
        });
        this.registerTorrentStatus('sickbeard_processing_completed_time', _('Processing Completed'), { colCfg:
            {
                sortable: true,
                renderer: function(value, metadata) {
                    if ( value != 9999999999 )
                        value = moment(value, "X").fromNow();
                    else
                        value = _('N/A');

                    metadata.attr = 'ext:qtip="Post-processing completed  ' + value + '"';

                    return value;
                },
                tooltip: _('Processing Completed')
            }
        });
        this.registerTorrentStatus('sickbeard_downloading', _('Downloading (cummulative time)'), {
            colCfg: {
                width: 45,
                sortable: true,
                renderer: function(value, metadata) {
                    value         = humanTime(value);
                    metadata.attr = 'ext:qtip="Torrent downloading for ' + value + '"';

                    return value;
                },
                tooltip: _('Downloading (cummulative time)')
            }
        });
        this.registerTorrentStatus('sickbeard_download_unavailable', _('Download Unavailable (cummulative time)'), {
            colCfg: {
                width: 45,
                sortable: true,
                renderer: function(value, metadata) {
                    value         = humanTime(value);
                    metadata.attr = 'ext:qtip="Torrent unavaialble for ' + value + '"';

                    return value;
                },
                tooltip: _('Download Unavailable (cummulative time)')
            }
        });
        this.registerTorrentStatus('sickbeard_time_added', _('Added (relative time)'), { colCfg:
            {
                sortable: true,
                renderer: function(value, metadata) {
                    if ( value != 9999999999 )
                        value = moment(value, "X").fromNow();
                    else
                        value = _('N/A');

                    metadata.attr = 'ext:qtip="Added  ' + value + '"';

                    return value;
                },
                tooltip: _('Added (relative time)')
            }
        });

        // Preferences page
        //
        this.prefsPage = deluge.preferences.addPage(new Deluge.ux.preferences.SickbeardPage());
	},

    onDisable: function() {
        console.log('Sickbeard plugin disabled');

        this.enabled = false;

        //this.toolbarBtn.disable();
        //this.toolbarBtn.hide();

        this.deregisterTorrentStatus('sickbeard_download_status'          , _('Download Status'));
        this.deregisterTorrentStatus('sickbeard_processing_status'        , _('Processing Status'));
        this.deregisterTorrentStatus('sickbeard_processing_completed_time', _('Processing Completed'));
        this.deregisterTorrentStatus('sickbeard_downloading'              , _('Downloading (hours)'));
        this.deregisterTorrentStatus('sickbeard_download_unavailable'     , _('Download Unavailable (hours)'));

        deluge.preferences.removePage(this.prefsPage);
    },

    onConnect: function() {
        if ( ! this.connected ) {
            console.log('Sickbeard: connected');

            this.connected = true;

            this.cachePatterns();

            this.toolbarBtn.enable();

            if (deluge.client.web) {
                console.log('Sickbeard: register event: post process completed');
            }

        } else { console.log('Sickbeard: already connected'); }
    },

    onDisconnect: function() {
        // onDisconnect seems to be called multiple times after logging out.
        // Prevent incorrect execution of code by checking this.connected.
        //
        if ( this.connected )
        {
            console.log('Sickbeard: disconnected');
            this.connected = false;
            this.toolbarBtn.disable();
        } else { console.log('Sickbeard: already disconnected'); }
    },

    onLogin: function() {
        if ( ! this.loggedin ) {
            console.log('Sickbeard: logged in');
            this.loggedin = true;
        } else { console.log('Sickbeard: already logged in'); }
    },

    onLogout: function() {
        // onLogout seems to be called multiple times after logging out
        // Prevent incorrect execution of code by checking this.loggedin.
        //
        if ( this.loggedin ) {
            console.log('Sickbeard: logged out');
            this.loggedin = false;
        } else { console.log('Sickbeard: already logged out'); }
    },

    processCompletedEvent: function(event) {
    },

    cachePatterns: function() {
        deluge.client.sickbeard.get_patterns({
            scope: this,
            success: function(patterns) {
                this.patterns_cache = patterns;
            }
        });
    },

    showDetails: function(task_id) {
        if (! this.dialogShowLog) {
            this.dialogShowLog = new Deluge.ux.Sickbeard.ShowLog();
        }
        output     = this.dialogShowLog.getComponent('output');
        form_left  = this.dialogShowLog.form_left;
        form_right = this.dialogShowLog.form_right;

        // Clean dialog content
        //
        form_left.getComponent('task_id').setValue(_('N/A'));
        form_left.getComponent('torrent_name').setValue(_('N/A'));
        form_left.getComponent('torrent_id').setValue(_('N/A'));
        form_left.getComponent('magnet').setValue(_('N/A'));
        form_left.getComponent('status').setValue(_('N/A'));

        form_right.getComponent('start_time').setValue(_('N/A'));
        form_right.getComponent('end_time').setValue(_('N/A'));
        form_right.getComponent('save_path').setValue(_('N/A'));
        form_right.getComponent('completed').setValue(_('N/A'));
        form_right.getComponent('size').setValue(_('N/A'));

        // Show dialog
        //
        this.dialogShowLog.show();

        output.update('Loading...');

        deluge.client.sickbeard.get_task(task_id, {
            scope: this,
            success: function(task) {
                form_left.getComponent('task_id').setValue(task.id);
                form_left.getComponent('torrent_name').setValue(task.torrent_info.name);
                form_left.getComponent('torrent_id').setValue(task.torrent_info.id);
                form_left.getComponent('magnet').setValue((task.torrent_info.magnet) ? task.torrent_info.magnet : _('N/A'));
                form_left.getComponent('status').setValue(task.status.capitalize());

                form_right.getComponent('start_time').setValue((task.start_time > 0) ? new Date(task.start_time * 1000).format("D M d Y H:i:s") : _('N/A'));
                form_right.getComponent('end_time').setValue((task.completed_time > 0) ? new Date(task.completed_time * 1000).format("D M d Y H:i:s") : _('N/A'));
                form_right.getComponent('save_path').setValue(task.torrent_info.options.download_location);
                form_right.getComponent('completed').setValue(((task.torrent_info.status.is_finished) ? 'Yes' : 'No'));
                form_right.getComponent('size').setValue(bytesToSize(task.torrent_info.status.total_size));

                lines = [];
                task.output.forEach(function(record){
                    lines.push(formatLogRecord(record, this.patterns_cache));
                }, this);

                output.update('<pre>' + lines.join('<br />') + '</pre>');

            },
            failure: function(failed) {
                output.update('Data could not be retrieved.');
            }
        });
    },

    process_success: function() {
        failed = false;
        this.process(failed);
    },

    process_failed: function() {
        failed = true;
        this.process(failed);
    },

    process: function(failed) {
        var ids = deluge.torrents.getSelectedIds();
        console.log(ids);
        deluge.client.sickbeard.add(ids, failed, {
            success: function(success) {
                console.log('Sickbeard: succesfully added job to queue')
                console.log(success)
                deluge.ui.update();

                if ( ! success )
                {
                    Ext.MessageBox.show({
                       title: 'Sickbeard post-processing failure.',
                       msg: 'Failed to add one ore more of the selected torrents to the post-processing queue.',
                       buttons: Ext.MessageBox.OK,
                       animateTarget: 'mb9',
                       icon: Ext.MessageBox.ERROR
                    });
                }
                else
                {
                    Ext.MessageBox.show({
                       title: 'Sickbeard post-processing success.',
                       msg: 'Successfully added all selected torrents to the post-processing queue.',
                       buttons: Ext.MessageBox.OK,
                       animateTarget: 'mb9',
                       icon: Ext.MessageBox.INFO
                    });
                }
            },
            failure: function() {
                console.log('Sickbeard: failed to add job to queue')
                Ext.MessageBox.show({
                   title: 'Sickbeard post-processing failure.',
                   msg: 'General failure adding one ore more of the selected torrents to the post-processing queue.',
                   buttons: Ext.MessageBox.OK,
                   animateTarget: 'mb9',
                   fn: showResult,
                   icon: Ext.MessageBox.ERROR
               });
            }
        });
    },

});

// Use this (older?) way of registering the plugin. Don't use the plugin class
// definition and initialization code of the create_plugin.py provided by
// Deluge themselves.
//
Deluge.registerPlugin('Sickbeard', Deluge.plugins.SickbeardPlugin);
