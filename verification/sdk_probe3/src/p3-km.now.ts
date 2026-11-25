import { action, Flow, wfa, trigger } from '@servicenow/sdk/automation'
Flow(
    { $id: Now.ID['p3_km'], name: 'TP3 KM', description: 'probe', runAs: 'system' },
    wfa.trigger(trigger.application.knowledgeManagement, { $id: Now.ID['p3_trig'] }, {}),
    (params) => {
        wfa.action(action.core.log, { $id: Now.ID['p3_log'] }, { log_level: 'info', log_message: `kb ${wfa.dataPill(params.trigger.knowledge.number, 'string')}` })
    }
)
Flow(
    { $id: Now.ID['p4_rt'], name: 'TP4 Remote', description: 'probe', runAs: 'system' },
    wfa.trigger(trigger.application.remoteTableQuery, { $id: Now.ID['p4_trig'] }, { u_table: 'v_st_recent_item' }),
    (params) => {
        wfa.action(action.core.log, { $id: Now.ID['p4_log'] }, { log_level: 'info', log_message: `q ${wfa.dataPill(params.trigger.query_id, 'string')}` })
    }
)
