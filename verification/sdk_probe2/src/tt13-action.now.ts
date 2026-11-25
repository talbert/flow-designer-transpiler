import { Action, actionStep, wfa } from '@servicenow/sdk/automation'
import { StringColumn } from '@servicenow/sdk/core'

export const tt13Action = Action(
    {
        $id: Now.ID['tt13_action'],
        name: 'TT13 Action',
        description: 'Transpiler comparison test. Reverses the input text with one Script step. Safe to delete.',
        inputs: {
            text: StringColumn({ label: 'Text' }),
        },
        outputs: {
            reversed: StringColumn({ label: 'Reversed' }),
        },
    },
    (params) => {
        const reverseStep = wfa.actionStep(
            actionStep.script,
            { $id: Now.ID['tt13_action_script_step'], label: 'Reverse text' },
            {
                required_run_time: 'instance',
                script: `(function execute(inputs, outputs) {
    outputs.reversed = String(inputs.text || '').split('').reverse().join('');
})(inputs, outputs);`,
                inputVariables: {
                    text: { label: 'Text', value: wfa.dataPill(params.inputs.text, 'string') },
                },
                outputVariables: {
                    reversed: StringColumn({ label: 'Reversed' }),
                },
            }
        )
        wfa.assignActionOutputs(params.outputs, {
            reversed: wfa.dataPill(reverseStep.reversed, 'string'),
        })
    }
)
