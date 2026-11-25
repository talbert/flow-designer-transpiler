import { action, Flow, wfa, trigger } from "@servicenow/sdk/automation";

Flow(
  {
    $id: Now.ID["tt11_sdk_probe_flow"],
    name: "TT11 SDK Probe Flow",
    description: "Transpiler comparison test. Written in Fluent, installed with the SDK. Runs for incidents whose short description starts with TT11RUN. Safe to delete.",
    runAs: "system"
  },
  wfa.trigger(
    trigger.record.created,
    { $id: Now.ID["tt11_incident_created"] },
    { table: "incident", condition: "short_descriptionSTARTSWITHTT11RUN", run_flow_in: "background" }
  ),
  params => {
    const admin = wfa.action(
      action.core.lookUpRecord,
      { $id: Now.ID["tt11_find_admin"] },
      { table: "sys_user", conditions: "user_name=admin" }
    );
    wfa.flowLogic.if(
      { $id: Now.ID["tt11_urgent"], condition: `${wfa.dataPill(params.trigger.current.urgency, "string")}=1` },
      () => {
        wfa.action(
          action.core.updateRecord,
          { $id: Now.ID["tt11_update_if"] },
          {
            table_name: "incident",
            record: wfa.dataPill(params.trigger.current.sys_id, "reference"),
            values: TemplateValue({ description: `SDK IF branch for ${wfa.dataPill(params.trigger.current.number, "string")} found ${wfa.dataPill(admin.Record.name, "string")}` })
          }
        );
      }
    );
    wfa.flowLogic.else({ $id: Now.ID["tt11_not_urgent"] }, () => {
      wfa.action(
        action.core.updateRecord,
        { $id: Now.ID["tt11_update_else"] },
        {
          table_name: "incident",
          record: wfa.dataPill(params.trigger.current.sys_id, "reference"),
          values: TemplateValue({ description: `SDK ELSE branch for ${wfa.dataPill(params.trigger.current.number, "string")}` })
        }
      );
    });
  }
);
