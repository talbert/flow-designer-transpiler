import { action, Flow, wfa, trigger } from '@servicenow/sdk/automation'
import { StringColumn } from '@servicenow/sdk/core'
import { tt13Subflow } from './tt13-subflow.now'
import { tt13Action } from './tt13-action.now'

Flow(
    {
        $id: Now.ID['tt13_compact_main'],
        name: 'TT13 Compact Main',
        description:
            'Transpiler comparison test. Runs for incidents whose short description starts with TT13RUN. Safe to delete.',
        runAs: 'system',
        flowVariables: {
            note: StringColumn({ label: 'Note' }),
        },
    },
    wfa.trigger(
        trigger.record.created,
        { $id: Now.ID['tt13_main_trigger'] },
        {
            table: 'incident',
            condition: 'short_descriptionSTARTSWITHTT13RUN',
            run_flow_in: 'background',
        }
    ),
    (params) => {
        // a. Look Up Records
        const users = wfa.action(
            action.core.lookUpRecords,
            { $id: Now.ID['tt13_main_lookup_users'] },
            {
                table: 'sys_user',
                conditions: 'user_nameINabel.tuter,itil',
            }
        )

        // b. Set Flow Variables
        wfa.flowLogic.setFlowVariables({ $id: Now.ID['tt13_main_set_note_start'] }, params.flowVariables, {
            note: 'start',
        })

        // c. For Each
        wfa.flowLogic.forEach(
            wfa.dataPill(users.Records, 'array.object'),
            { $id: Now.ID['tt13_main_for_each_user'] },
            (item) => {
                wfa.flowLogic.setFlowVariables({ $id: Now.ID['tt13_main_set_note_append'] }, params.flowVariables, {
                    note: `${wfa.dataPill(params.flowVariables.note, 'string')} +${wfa.dataPill(item.user_name, 'string')}`,
                })
            }
        )

        // d. If / Else If / Else
        wfa.flowLogic.if(
            {
                $id: Now.ID['tt13_main_if_urgency_1'],
                condition: `${wfa.dataPill(params.trigger.current.urgency, 'string')}=1`,
            },
            () => {
                wfa.action(
                    action.core.updateRecord,
                    { $id: Now.ID['tt13_main_update_if'] },
                    {
                        table_name: 'incident',
                        record: wfa.dataPill(params.trigger.current, 'reference'),
                        values: TemplateValue({
                            description: `TT13 IF branch for ${wfa.dataPill(params.trigger.current.number, 'string')}`,
                        }),
                    }
                )
            }
        )
        wfa.flowLogic.elseIf(
            {
                $id: Now.ID['tt13_main_else_if_urgency_2'],
                condition: `${wfa.dataPill(params.trigger.current.urgency, 'string')}=2`,
            },
            () => {
                wfa.action(
                    action.core.updateRecord,
                    { $id: Now.ID['tt13_main_update_else_if'] },
                    {
                        table_name: 'incident',
                        record: wfa.dataPill(params.trigger.current, 'reference'),
                        values: TemplateValue({
                            description: `TT13 ELSE IF branch for ${wfa.dataPill(params.trigger.current.number, 'string')}`,
                        }),
                    }
                )
            }
        )
        wfa.flowLogic.else({ $id: Now.ID['tt13_main_else'] }, () => {
            wfa.action(
                action.core.updateRecord,
                { $id: Now.ID['tt13_main_update_else'] },
                {
                    table_name: 'incident',
                    record: wfa.dataPill(params.trigger.current, 'reference'),
                    values: TemplateValue({
                        description: `TT13 ELSE branch for ${wfa.dataPill(params.trigger.current.number, 'string')}`,
                    }),
                }
            )
        })

        // e. Call the subflow
        const sub = wfa.subflow(
            tt13Subflow,
            { $id: Now.ID['tt13_main_call_subflow'] },
            {
                user_name: wfa.dataPill(params.trigger.current.caller_id.user_name, 'string'),
                waitForCompletion: true,
            }
        )

        // f. Call the custom action
        const reversedResult = wfa.action(
            tt13Action,
            { $id: Now.ID['tt13_main_call_action'] },
            {
                text: wfa.dataPill(sub.found, 'string'),
            }
        )

        // g. Try / Catch
        wfa.flowLogic.tryCatch(
            { $id: Now.ID['tt13_main_try_catch'] },
            {
                try: () => {
                    wfa.action(
                        action.core.lookUpRecord,
                        { $id: Now.ID['tt13_main_try_lookup'] },
                        {
                            table: 'sys_user',
                            conditions: 'user_name=tt13_no_such_user',
                            dont_fail_flow_on_error: false,
                        }
                    )
                    wfa.action(
                        action.core.updateRecord,
                        { $id: Now.ID['tt13_main_try_update'] },
                        {
                            table_name: 'incident',
                            record: wfa.dataPill(params.trigger.current, 'reference'),
                            values: TemplateValue({
                                close_notes: 'TT13 try finished',
                            }),
                        }
                    )
                },
                catch: () => {
                    wfa.action(
                        action.core.createRecord,
                        { $id: Now.ID['tt13_main_catch_create'] },
                        {
                            table_name: 'incident_task',
                            values: TemplateValue({
                                incident: wfa.dataPill(params.trigger.current.sys_id, 'string'),
                                short_description: 'TT13 caught',
                            }),
                        }
                    )
                },
            }
        )

        // h. Do the following in Parallel
        wfa.flowLogic.doInParallel(
            { $id: Now.ID['tt13_main_parallel'] },
            () => {
                wfa.action(
                    action.core.createRecord,
                    { $id: Now.ID['tt13_main_parallel_a'] },
                    {
                        table_name: 'incident_task',
                        values: TemplateValue({
                            incident: wfa.dataPill(params.trigger.current.sys_id, 'string'),
                            short_description: 'TT13 branch A',
                        }),
                    }
                )
            },
            () => {
                wfa.action(
                    action.core.createRecord,
                    { $id: Now.ID['tt13_main_parallel_b'] },
                    {
                        table_name: 'incident_task',
                        values: TemplateValue({
                            incident: wfa.dataPill(params.trigger.current.sys_id, 'string'),
                            short_description: 'TT13 branch B',
                        }),
                    }
                )
            }
        )

        // i. Wait for a duration
        wfa.flowLogic.waitForADuration({
            $id: Now.ID['tt13_main_wait_5s'],
            durationType: 'explicit_duration',
            duration: Duration({ seconds: 5 }),
        })

        // j. Final Update Record
        wfa.action(
            action.core.updateRecord,
            { $id: Now.ID['tt13_main_update_final'] },
            {
                table_name: 'incident',
                record: wfa.dataPill(params.trigger.current, 'reference'),
                values: TemplateValue({
                    work_notes: `TT13 var [${wfa.dataPill(params.flowVariables.note, 'string')}] subflow [${wfa.dataPill(sub.found, 'string')}] action [${wfa.dataPill(reversedResult.reversed, 'string')}]`,
                }),
            }
        )
    }
)
