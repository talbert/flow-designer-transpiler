import { action, Flow, wfa, trigger } from '@servicenow/sdk/automation'

Flow(
    {
        $id: Now.ID['tt13_compact_daily'],
        name: 'TT13 Compact Daily',
        description: 'Transpiler comparison test. Scheduled Daily trigger at 03:40:00. Safe to delete.',
    },
    wfa.trigger(
        trigger.scheduled.daily,
        { $id: Now.ID['tt13_daily_trigger'] },
        {
            time: Time({ hours: 3, minutes: 40, seconds: 0 }, 'UTC'),
        }
    ),
    (_params) => {
        wfa.action(
            action.core.lookUpRecord,
            { $id: Now.ID['tt13_daily_find_admin'] },
            {
                table: 'sys_user',
                conditions: 'user_name=admin',
            }
        )
    }
)
