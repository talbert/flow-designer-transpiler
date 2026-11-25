import { action, Flow, wfa, trigger } from '@servicenow/sdk/automation'

Flow(
    {
        $id: Now.ID['tt13_compact_catalog'],
        name: 'TT13 Compact Catalog',
        description: 'Transpiler comparison test. Service Catalog trigger with a catalog variable. Safe to delete.',
    },
    wfa.trigger(trigger.application.serviceCatalog, { $id: Now.ID['tt13_catalog_trigger'] }, {}),
    (params) => {
        const vars = wfa.action(
            action.core.getCatalogVariables,
            { $id: Now.ID['tt13_catalog_get_variables'] },
            {
                requested_item: wfa.dataPill(params.trigger.request_item, 'reference'),
                template_catalog_item: '439fef5b83e41310d6401665eeaad379',
                catalog_variables: '9f9fef5b83e41310d6401665eeaad3b3:item_option_new',
            }
        )

        wfa.action(
            action.core.createCatalogTask,
            { $id: Now.ID['tt13_catalog_create_task'] },
            {
                ah_requested_item: wfa.dataPill(params.trigger.request_item, 'reference'),
                ah_short_description: `TT13 task, note [${wfa.dataPill(vars.tt9_note, 'string')}]`,
                ah_wait: false,
            }
        )

        wfa.action(
            action.core.updateRecord,
            { $id: Now.ID['tt13_catalog_update_ritm'] },
            {
                table_name: 'sc_req_item',
                record: wfa.dataPill(params.trigger.request_item, 'reference'),
                values: TemplateValue({
                    description: `TT13 catalog flow ran, note [${wfa.dataPill(vars.tt9_note, 'string')}]`,
                }),
            }
        )
    }
)
