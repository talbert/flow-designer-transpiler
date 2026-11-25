import { action, Flow, wfa, trigger } from '@servicenow/sdk/automation'
Flow(
    { $id: Now.ID['p6_misc'], name: 'TP6 Misc', description: 'probe', runAs: 'system' },
    wfa.trigger(trigger.record.created, { $id: Now.ID['p6_trig'] }, { table: 'incident', condition: 'short_descriptionSTARTSWITHTP6', run_flow_in: 'background' }),
    (params) => {
        const w = wfa.action(action.core.waitForCondition, { $id: Now.ID['p6_wait'] }, {
            record: `${wfa.dataPill(params.trigger.current, 'reference')}`, table_name: 'incident', conditions: 'state=2',
            timeout_flag: true, timeout_duration: Duration({ minutes: 5 }),
        })
        const m = wfa.action(action.core.waitForMessage, { $id: Now.ID['p6_msg'] }, { message: 'TT21MSG', enable_timeout: true, timeout: Duration({ seconds: 15 }) })
        const r = wfa.action(action.core.submitCatalogItemRequest, { $id: Now.ID['p6_sub'] }, {
            catalog_item: '439fef5b83e41310d6401665eeaad379', catalog_item_inputs: 'tt9_note=hello', sysparm_quantity: 1, wait_for_completion: false,
            sysparm_requested_for: '62826bf03710200044e0bfc8bcbe5df1',
        })
        const g = wfa.action(action.core.getAttachmentsOnRecord, { $id: Now.ID['p6_ga'] }, { source_record: `${wfa.dataPill(params.trigger.current, 'reference')}` })
        wfa.flowLogic.forEach(wfa.dataPill(g.parameter, 'array.object'), { $id: Now.ID['p6_fe'] }, (item) => {
            wfa.action(action.core.copyAttachment, { $id: Now.ID['p6_cp'] }, {
                table: 'incident', target_record: wfa.dataPill(params.trigger.current, 'reference'), attachment_record: wfa.dataPill(item, 'reference'),
            })
        })
        wfa.action(action.core.deleteAttachment, { $id: Now.ID['p6_del'] }, { table: 'incident', record: wfa.dataPill(params.trigger.current, 'reference'), delete_all_: false, attachment_file_name: 'x.txt' })
        wfa.action(action.core.sendSms, { $id: Now.ID['p6_sms'] }, { recipients: '+13035550100', message: `state ${wfa.dataPill(w.state, 'string')} payload ${wfa.dataPill(m.payload, 'string')} ritm ${wfa.dataPill(r.requested_item, 'reference')}` })
    }
)
