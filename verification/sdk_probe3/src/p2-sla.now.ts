import { action, Flow, wfa, trigger } from '@servicenow/sdk/automation'
Flow(
    { $id: Now.ID['p2_sla'], name: 'TP2 SLA', description: 'probe', runAs: 'system' },
    wfa.trigger(trigger.application.slaTask, { $id: Now.ID['p2_trig'] }, {}),
    (params) => {
        const t = wfa.action(action.core.slaPercentageTimer, { $id: Now.ID['p2_timer'] }, {
            percentage: 50,
        })
        wfa.action(action.core.log, { $id: Now.ID['p2_log'] }, {
            log_level: 'info',
            log_message: `status ${wfa.dataPill(t.status, 'string')} task ${wfa.dataPill(params.trigger.task_sla_record.task.number, 'string')} name ${wfa.dataPill(params.trigger.sla_flow_inputs.name, 'string')}`,
        })
    }
)
