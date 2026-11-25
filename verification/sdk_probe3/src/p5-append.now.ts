import { action, Flow, wfa, trigger, FlowArray, FlowObject } from '@servicenow/sdk/automation'
import { StringColumn, IntegerColumn } from '@servicenow/sdk/core'
Flow(
    {
        $id: Now.ID['p5_append'], name: 'TT22C Append To Flow Variables', description: 'Transpiler test 22. Append to Flow Variables on an array of objects, built by the Fluent SDK. Runs for incidents whose short description starts with TT22C RUN. Safe to delete.', runAs: 'system',
        flowVariables: {
            items: FlowArray({ label: 'Items', mandatory: false, childName: 'item',
                elementType: FlowObject({ label: 'Item', mandatory: false, fields: { name: StringColumn({ label: 'Name' }), id: IntegerColumn({ label: 'ID' }) } }) }),
        },
    },
    wfa.trigger(trigger.record.createdOrUpdated, { $id: Now.ID['p5_trig'] }, { table: 'incident', condition: 'short_descriptionSTARTSWITHTT22C RUN', run_flow_in: 'background', trigger_strategy: 'once' }),
    (params) => {
        wfa.flowLogic.appendToFlowVariables({ $id: Now.ID['p5_a1'] }, params.flowVariables, { items: { name: 'Alice', id: 1 } })
        wfa.flowLogic.appendToFlowVariables({ $id: Now.ID['p5_a2'] }, params.flowVariables, { items: { name: `${wfa.dataPill(params.trigger.current.number, 'string')}`, id: 2 } })
        wfa.flowLogic.forEach(wfa.dataPill(params.flowVariables.items, 'array.object'), { $id: Now.ID['p5_fe'] }, (item) => {
            wfa.action(action.core.log, { $id: Now.ID['p5_log'] }, { log_level: 'info', log_message: `TT22C item [${wfa.dataPill(item.name, 'string')}] id [${wfa.dataPill(item.id, 'integer')}]` })
        })
    }
)
