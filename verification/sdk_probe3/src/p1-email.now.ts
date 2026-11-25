import { action, Flow, wfa, trigger } from '@servicenow/sdk/automation'
Flow(
    { $id: Now.ID['p1_email'], name: 'TP1 Email', description: 'probe', runAs: 'system' },
    wfa.trigger(trigger.application.inboundEmail, { $id: Now.ID['p1_trig'] }, {
        email_conditions: 'subjectLIKETT21MAIL', order: 50, stop_condition_evaluation: true, target_table: 'incident',
    }),
    (params) => {
        const h = wfa.action(action.core.getEmailHeader, { $id: Now.ID['p1_hdr'] }, {
            target_header: 'X-TT21', email_record: wfa.dataPill(params.trigger.inbound_email, 'reference'),
        })
        const t = wfa.action(action.core.getLatestResponseTextFromEmail, { $id: Now.ID['p1_txt'] }, {
            email_record: wfa.dataPill(params.trigger.inbound_email, 'reference'),
        })
        const a = wfa.action(action.core.lookUpEmailAttachments, { $id: Now.ID['p1_att'] }, {
            email_record: wfa.dataPill(params.trigger.inbound_email, 'reference'),
        })
        wfa.action(action.core.log, { $id: Now.ID['p1_log'] }, {
            log_level: 'info',
            log_message: `hdr ${wfa.dataPill(h.header_value, 'string')} txt ${wfa.dataPill(t.latest_response_text, 'string')} subj ${wfa.dataPill(params.trigger.subject, 'string')} from ${wfa.dataPill(params.trigger.from_address, 'string')} att ${wfa.dataPill(a.email_attachments, 'array.object')}`,
        })
    }
)
