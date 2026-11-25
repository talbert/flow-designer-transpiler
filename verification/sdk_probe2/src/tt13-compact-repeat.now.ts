import { action, Flow, wfa, trigger } from '@servicenow/sdk/automation'

Flow(
    {
        $id: Now.ID['tt13_compact_repeat'],
        name: 'TT13 Compact Repeat',
        description: 'Transpiler comparison test. Scheduled Repeat trigger, every 2 minutes. Safe to delete.',
    },
    wfa.trigger(
        trigger.scheduled.repeat,
        { $id: Now.ID['tt13_repeat_trigger'] },
        {
            repeat: Duration({ minutes: 2 }),
        }
    ),
    (_params) => {
        wfa.action(
            action.core.lookUpRecord,
            { $id: Now.ID['tt13_repeat_find_admin'] },
            {
                table: 'sys_user',
                conditions: 'user_name=admin',
            }
        )
    }
)
