import { action, Subflow, wfa } from '@servicenow/sdk/automation'
import { StringColumn } from '@servicenow/sdk/core'

export const tt13Subflow = Subflow(
    {
        $id: Now.ID['tt13_subflow'],
        name: 'TT13 Subflow',
        description:
            'Transpiler comparison test. Looks up a sys_user by user name and returns the name. Safe to delete.',
        inputs: {
            user_name: StringColumn({ label: 'User name', mandatory: true }),
        },
        outputs: {
            found: StringColumn({ label: 'Found' }),
        },
    },
    (params) => {
        const user = wfa.action(
            action.core.lookUpRecord,
            { $id: Now.ID['tt13_subflow_find_user'] },
            {
                table: 'sys_user',
                conditions: `user_name=${wfa.dataPill(params.inputs.user_name, 'string')}`,
            }
        )
        wfa.flowLogic.assignSubflowOutputs({ $id: Now.ID['tt13_subflow_assign_outputs'] }, params.outputs, {
            found: wfa.dataPill(user.Record.name, 'string'),
        })
    }
)
