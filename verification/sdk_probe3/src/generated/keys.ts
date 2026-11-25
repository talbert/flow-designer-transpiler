import '@servicenow/sdk/global'

declare global {
    namespace Now {
        namespace Internal {
            interface Keys extends KeysRegistry {
                explicit: {
                    bom_json: {
                        table: 'sys_module'
                        id: '3fcec15c81c34eed9b5054c90392a54b'
                    }
                    p1_att: {
                        table: 'sys_hub_action_instance_v2'
                        id: 'd74a7a3977fd47bbb3b1f4f56e4813cb'
                    }
                    p1_email: {
                        table: 'sys_hub_flow'
                        id: 'ab0a3507497f4f2eb35bc5deff4493ca'
                    }
                    p1_hdr: {
                        table: 'sys_hub_action_instance_v2'
                        id: '6b1374e95e5849b39600ae55e44c31d2'
                    }
                    p1_log: {
                        table: 'sys_hub_action_instance_v2'
                        id: 'e36169dbaab545aa9b6cd431f568ab4a'
                    }
                    p1_trig: {
                        table: 'sys_hub_trigger_instance_v2'
                        id: 'a676d1d8e03c4b989c5a1762a157d0d5'
                    }
                    p1_txt: {
                        table: 'sys_hub_action_instance_v2'
                        id: '21040c9f4d434fda80ba84ad773d0797'
                    }
                    p2_log: {
                        table: 'sys_hub_action_instance_v2'
                        id: 'c91b3a7e949f4db48bea2084447629b8'
                    }
                    p2_sla: {
                        table: 'sys_hub_flow'
                        id: '9ac85942dabe4a08a0578cda0fe01729'
                    }
                    p2_timer: {
                        table: 'sys_hub_action_instance_v2'
                        id: '551796d8d8e745b5bedbdb9be1e46e64'
                    }
                    p2_trig: {
                        table: 'sys_hub_trigger_instance_v2'
                        id: 'd63fa6290ef447f38907521636ea420e'
                    }
                    p3_km: {
                        table: 'sys_hub_flow'
                        id: '0b158bf450c043c6adb930f87f6c2037'
                    }
                    p3_log: {
                        table: 'sys_hub_action_instance_v2'
                        id: '22cd4616d6be4b61b47b5fb540217012'
                    }
                    p3_trig: {
                        table: 'sys_hub_trigger_instance_v2'
                        id: '854c4e91bcce4573bb0eb12cacbef6c9'
                    }
                    p4_log: {
                        table: 'sys_hub_action_instance_v2'
                        id: '81215e1590ad4e45a5023d91787744ca'
                    }
                    p4_rt: {
                        table: 'sys_hub_flow'
                        id: '5557eb40be484369b5762dacaf647fbb'
                    }
                    p4_trig: {
                        table: 'sys_hub_trigger_instance_v2'
                        id: '9d0cfd25a1834b86b4123dac7c063e54'
                    }
                    p5_a1: {
                        table: 'sys_hub_flow_logic_instance_v2'
                        id: 'a1afba251a7d46b8a467812c5024a9ff'
                    }
                    p5_a2: {
                        table: 'sys_hub_flow_logic_instance_v2'
                        id: '23ed368a4e974a0fb6b67ed3772ee6e9'
                    }
                    p5_append: {
                        table: 'sys_hub_flow'
                        id: '341eca5f2ad64e15b5f6037e2bbd91d9'
                    }
                    p5_fe: {
                        table: 'sys_hub_flow_logic_instance_v2'
                        id: '8d5389b0bd6449dea031d471771f518a'
                    }
                    p5_log: {
                        table: 'sys_hub_action_instance_v2'
                        id: 'b45cf771ca2b4f3ea063d6222388298f'
                    }
                    p5_trig: {
                        table: 'sys_hub_trigger_instance_v2'
                        id: '987041a518674436ab1b9d34ce8ac1e4'
                    }
                    p6_cp: {
                        table: 'sys_hub_action_instance_v2'
                        id: '6c4bb88f7e994c4789a6c33c1ff0ad92'
                    }
                    p6_del: {
                        table: 'sys_hub_action_instance_v2'
                        id: 'eefb319628a74468ad0f3ce325cd935a'
                    }
                    p6_fe: {
                        table: 'sys_hub_flow_logic_instance_v2'
                        id: 'b6e36db2e126442dbd5997d37c272939'
                    }
                    p6_ga: {
                        table: 'sys_hub_action_instance_v2'
                        id: 'd380bff39bb04617822c147204d9e916'
                    }
                    p6_misc: {
                        table: 'sys_hub_flow'
                        id: 'e6636f41300d4273be6a351c85f1db59'
                    }
                    p6_msg: {
                        table: 'sys_hub_action_instance_v2'
                        id: '5ea0bba133b941b1930d50579e8a99a2'
                    }
                    p6_sms: {
                        table: 'sys_hub_action_instance_v2'
                        id: '496b0aafcff14c3ea6cc6ce4f55b54f2'
                    }
                    p6_sub: {
                        table: 'sys_hub_action_instance_v2'
                        id: '7bbac942957040009c3ff90bfa573c84'
                    }
                    p6_trig: {
                        table: 'sys_hub_trigger_instance_v2'
                        id: '595105eb04844e7395fa325246839b6c'
                    }
                    p6_wait: {
                        table: 'sys_hub_action_instance_v2'
                        id: '73f93898141e46b3aa82075840be4b62'
                    }
                    package_json: {
                        table: 'sys_module'
                        id: '59deef52aaf14651bfd3129108701b82'
                    }
                    tt13_action: {
                        table: 'sys_hub_action_type_definition'
                        id: '6808a80282a048d0899a7819b3f38e4b'
                        deleted: true
                    }
                    tt13_action_script_step: {
                        table: 'sys_hub_step_instance'
                        id: '5e58e21c02d341ae97f3976afbd88d7e'
                        deleted: true
                    }
                    tt13_catalog_create_task: {
                        table: 'sys_hub_action_instance_v2'
                        id: 'e25aea9ae69a4232a7e5f11a63fd4832'
                        deleted: true
                    }
                    tt13_catalog_get_variables: {
                        table: 'sys_hub_action_instance_v2'
                        id: '24ec0b2ab65e483ca8fb20ccf9b422f0'
                        deleted: true
                    }
                    tt13_catalog_trigger: {
                        table: 'sys_hub_trigger_instance_v2'
                        id: 'daa1661f03b9417499bbd81cf74b7783'
                        deleted: true
                    }
                    tt13_catalog_update_ritm: {
                        table: 'sys_hub_action_instance_v2'
                        id: '29bfbe1a395b4c0c873efefffcdf632e'
                        deleted: true
                    }
                    tt13_compact_catalog: {
                        table: 'sys_hub_flow'
                        id: '421af7af6e3f498fa1404e41e137fad6'
                        deleted: true
                    }
                    tt13_compact_daily: {
                        table: 'sys_hub_flow'
                        id: 'cb8e946cc1b24aaba8505e4d6c142c46'
                        deleted: true
                    }
                    tt13_compact_main: {
                        table: 'sys_hub_flow'
                        id: 'dd0fabad027a44938069bc23381dd1b1'
                        deleted: true
                    }
                    tt13_compact_repeat: {
                        table: 'sys_hub_flow'
                        id: 'aa00fed33d4a4d0c9e0d078aef57bf2a'
                        deleted: true
                    }
                    tt13_daily_find_admin: {
                        table: 'sys_hub_action_instance_v2'
                        id: 'c51e5394292b48e9bf361e30fce5e383'
                        deleted: true
                    }
                    tt13_daily_trigger: {
                        table: 'sys_hub_trigger_instance_v2'
                        id: 'b0abb4340aaf4ec0a9952d9c3c78a4b1'
                        deleted: true
                    }
                    tt13_main_call_action: {
                        table: 'sys_hub_action_instance_v2'
                        id: '68bd9cfe6b9f4f38b0f3e8f4f829522b'
                        deleted: true
                    }
                    tt13_main_call_subflow: {
                        table: 'sys_hub_sub_flow_instance_v2'
                        id: '88d0874d30e24da5bbcb6f27cb75d179'
                        deleted: true
                    }
                    tt13_main_catch_create: {
                        table: 'sys_hub_action_instance_v2'
                        id: '28721d09f3a2461cb2d42d7495208cea'
                        deleted: true
                    }
                    tt13_main_else: {
                        table: 'sys_hub_flow_logic_instance_v2'
                        id: 'ee27ec87c09c4032937deb658fa6595a'
                        deleted: true
                    }
                    tt13_main_else_if_urgency_2: {
                        table: 'sys_hub_flow_logic_instance_v2'
                        id: '7805f8ecbcef4fe7b1179f416c8ed167'
                        deleted: true
                    }
                    tt13_main_for_each_user: {
                        table: 'sys_hub_flow_logic_instance_v2'
                        id: 'e7b5c8a2587448a494817e3cd650a39a'
                        deleted: true
                    }
                    tt13_main_if_urgency_1: {
                        table: 'sys_hub_flow_logic_instance_v2'
                        id: '6082131721184579b1e186b5b074237d'
                        deleted: true
                    }
                    tt13_main_lookup_users: {
                        table: 'sys_hub_action_instance_v2'
                        id: '12f86fa68612463abce73fb7082fc51a'
                        deleted: true
                    }
                    tt13_main_parallel: {
                        table: 'sys_hub_flow_logic_instance_v2'
                        id: 'b3f3819c9ed94766ad1488f8831f0d8e'
                        deleted: true
                    }
                    tt13_main_parallel_a: {
                        table: 'sys_hub_action_instance_v2'
                        id: 'f4b0d8fc2a8146ab97a0a2bd9a51afa1'
                        deleted: true
                    }
                    tt13_main_parallel_b: {
                        table: 'sys_hub_action_instance_v2'
                        id: 'c39e2da5c281488795d27e5708920ee8'
                        deleted: true
                    }
                    tt13_main_parallel_block_0: {
                        table: 'sys_hub_flow_logic_instance_v2'
                        id: '6bb0aac636694abbb24365d888806256'
                        deleted: true
                    }
                    tt13_main_parallel_block_1: {
                        table: 'sys_hub_flow_logic_instance_v2'
                        id: 'e46dc17d559244679df98edca7620172'
                        deleted: true
                    }
                    tt13_main_set_note_append: {
                        table: 'sys_hub_flow_logic_instance_v2'
                        id: '981bc035686441b3a64c9a82085a1968'
                        deleted: true
                    }
                    tt13_main_set_note_start: {
                        table: 'sys_hub_flow_logic_instance_v2'
                        id: '9e1a3ff91da941a18a841e1a4c580454'
                        deleted: true
                    }
                    tt13_main_trigger: {
                        table: 'sys_hub_trigger_instance_v2'
                        id: 'e00e937438064db3a0af112ecc24376b'
                        deleted: true
                    }
                    tt13_main_try_catch: {
                        table: 'sys_hub_flow_logic_instance_v2'
                        id: 'e027a4e214b34920983d954d0cff9da3'
                        deleted: true
                    }
                    tt13_main_try_catch_catch: {
                        table: 'sys_hub_flow_logic_instance_v2'
                        id: '75cc8909236c410587edcb2b20063d30'
                        deleted: true
                    }
                    tt13_main_try_lookup: {
                        table: 'sys_hub_action_instance_v2'
                        id: 'e40b1777df494278810a1ed7fc8eee80'
                        deleted: true
                    }
                    tt13_main_try_update: {
                        table: 'sys_hub_action_instance_v2'
                        id: 'ca95e3a8f02c4940877e2843665a22bc'
                        deleted: true
                    }
                    tt13_main_update_else: {
                        table: 'sys_hub_action_instance_v2'
                        id: '162ae53014cd4dbab64ae0a444704f81'
                        deleted: true
                    }
                    tt13_main_update_else_if: {
                        table: 'sys_hub_action_instance_v2'
                        id: '7efbe732c9a84a6c864ac29246229be1'
                        deleted: true
                    }
                    tt13_main_update_final: {
                        table: 'sys_hub_action_instance_v2'
                        id: 'fcbab2201c1f4f11bc719d767082274b'
                        deleted: true
                    }
                    tt13_main_update_if: {
                        table: 'sys_hub_action_instance_v2'
                        id: 'da41bf56a0fc402583f7ac0d4a243ab0'
                        deleted: true
                    }
                    tt13_main_wait_5s: {
                        table: 'sys_hub_flow_logic_instance_v2'
                        id: '59a844f003cb466684cb1a6641da27a6'
                        deleted: true
                    }
                    tt13_repeat_find_admin: {
                        table: 'sys_hub_action_instance_v2'
                        id: '5dcaa844b9e14cb49e80bff69b57969c'
                        deleted: true
                    }
                    tt13_repeat_trigger: {
                        table: 'sys_hub_trigger_instance_v2'
                        id: '4bf949addc8742b5ac83924aa83daeb0'
                        deleted: true
                    }
                    tt13_subflow: {
                        table: 'sys_hub_flow'
                        id: 'f0124e5ade0346d099c6b01d2bed9524'
                        deleted: true
                    }
                    tt13_subflow_assign_outputs: {
                        table: 'sys_hub_flow_logic_instance_v2'
                        id: '76657fed15ea4354b769c515fad2c6c3'
                        deleted: true
                    }
                    tt13_subflow_find_user: {
                        table: 'sys_hub_action_instance_v2'
                        id: 'a1ca6b09c4304885852fb7b4ce471b09'
                        deleted: true
                    }
                }
                composite: [
                    {
                        table: 'sys_hub_flow_input'
                        id: '064b0fea9d4947c5821c7307e529dbf2'
                        deleted: true
                        key: {
                            model: 'f0124e5ade0346d099c6b01d2bed9524'
                            element: 'user_name'
                        }
                    },
                    {
                        table: 'sys_documentation'
                        id: '0be17e9163124a27a60d75322578f981'
                        deleted: true
                        key: {
                            name: 'var__m_sys_hub_flow_output_f0124e5ade0346d099c6b01d2bed9524'
                            element: 'found'
                            language: 'en'
                        }
                    },
                    {
                        table: 'sys_hub_action_output'
                        id: '372e541f82f44b08a6f0fb16a9c29ca3'
                        deleted: true
                        key: {
                            model: '6808a80282a048d0899a7819b3f38e4b'
                            element: '__dont_treat_as_error__'
                        }
                    },
                    {
                        table: 'sys_hub_action_output'
                        id: '3d7350cf5fa84bfc9c47724ec8411d13'
                        deleted: true
                        key: {
                            model: '6808a80282a048d0899a7819b3f38e4b'
                            element: '__action_status__'
                        }
                    },
                    {
                        table: 'sys_complex_object'
                        id: '581f169ddd524c96971a507cb6cac522'
                        key: {
                            name: 'FDb09b14dd2a5647738a680ec184cc6d3f'
                        }
                    },
                    {
                        table: 'sys_hub_flow_variable'
                        id: '64b6d789f19c46e789769480c1791ff3'
                        deleted: true
                        key: {
                            model: 'dd0fabad027a44938069bc23381dd1b1'
                            element: 'note'
                        }
                    },
                    {
                        table: 'sys_documentation'
                        id: '65e4ad3d03c2450d8bb324442b9e0e69'
                        key: {
                            name: 'var__m_sys_hub_flow_variable_341eca5f2ad64e15b5f6037e2bbd91d9'
                            element: 'items'
                            language: 'en'
                        }
                    },
                    {
                        table: 'sys_documentation'
                        id: '6ea462d3ff7c4a678e8312b2456f57a4'
                        deleted: true
                        key: {
                            name: 'var__m_sys_hub_action_input_6808a80282a048d0899a7819b3f38e4b'
                            element: 'text'
                            language: 'en'
                        }
                    },
                    {
                        table: 'sys_documentation'
                        id: '70273c526ecd4d6ba7a77c8388407b45'
                        deleted: true
                        key: {
                            name: 'var__m_sys_hub_action_output_6808a80282a048d0899a7819b3f38e4b'
                            element: '__action_status__'
                            language: 'en'
                        }
                    },
                    {
                        table: 'sys_variable_value'
                        id: '96aa4e948dd7429b8a0b0d0710e878c5'
                        deleted: true
                        key: {
                            document_key: '5e58e21c02d341ae97f3976afbd88d7e'
                            variable: '74315b04b3201300176b051a16a8dc2b'
                        }
                    },
                    {
                        table: 'sys_documentation'
                        id: 'a1fa692511c4405e918d9c0c1849bf7a'
                        deleted: true
                        key: {
                            name: 'var__m_sys_hub_action_output_6808a80282a048d0899a7819b3f38e4b'
                            element: '__dont_treat_as_error__'
                            language: 'en'
                        }
                    },
                    {
                        table: 'sys_documentation'
                        id: 'a2c5206afb8e428f875297023d069201'
                        deleted: true
                        key: {
                            name: 'var__m_sys_hub_flow_input_f0124e5ade0346d099c6b01d2bed9524'
                            element: 'user_name'
                            language: 'en'
                        }
                    },
                    {
                        table: 'sys_hub_flow_variable'
                        id: 'b09b14dd2a5647738a680ec184cc6d3f'
                        key: {
                            model: '341eca5f2ad64e15b5f6037e2bbd91d9'
                            element: 'items'
                        }
                    },
                    {
                        table: 'sys_variable_value'
                        id: 'b4364611530a47de96052f39a5cfae0f'
                        deleted: true
                        key: {
                            document_key: '5e58e21c02d341ae97f3976afbd88d7e'
                            variable: '71aa7f6647032200b4fad7527c9a719b'
                        }
                    },
                    {
                        table: 'sys_hub_action_output'
                        id: 'bfce6f8d0510410d97188a1adbb5ddfd'
                        deleted: true
                        key: {
                            model: '6808a80282a048d0899a7819b3f38e4b'
                            element: 'reversed'
                        }
                    },
                    {
                        table: 'sys_hub_step_ext_input'
                        id: 'c289f710a414403db8ced590063bdd01'
                        deleted: true
                        key: {
                            model: '5e58e21c02d341ae97f3976afbd88d7e'
                            element: 'text'
                        }
                    },
                    {
                        table: 'sys_hub_action_input'
                        id: 'c9a42adb64e34b1c98752eaa6213ac04'
                        deleted: true
                        key: {
                            model: '6808a80282a048d0899a7819b3f38e4b'
                            element: 'text'
                        }
                    },
                    {
                        table: 'sys_documentation'
                        id: 'cdcbd1eaa22c4c499fd88e4d17ae7f30'
                        deleted: true
                        key: {
                            name: 'var__m_sys_hub_flow_variable_dd0fabad027a44938069bc23381dd1b1'
                            element: 'note'
                            language: 'en'
                        }
                    },
                    {
                        table: 'sys_hub_flow_output'
                        id: 'd54414dd1b0e477393d1fd9a8a6a27a3'
                        deleted: true
                        key: {
                            model: 'f0124e5ade0346d099c6b01d2bed9524'
                            element: 'found'
                        }
                    },
                    {
                        table: 'sys_element_mapping'
                        id: 'd674fca76d7c4784a6aab3df35b7e416'
                        deleted: true
                        key: {
                            id: '6808a80282a048d0899a7819b3f38e4b'
                            table: 'var__m_sys_hub_action_output_6808a80282a048d0899a7819b3f38e4b'
                            field: 'reversed'
                        }
                    },
                    {
                        table: 'sys_documentation'
                        id: 'e08b380aeca24b4687f3024fc203f7c2'
                        deleted: true
                        key: {
                            name: 'var__m_sys_hub_action_output_6808a80282a048d0899a7819b3f38e4b'
                            element: 'reversed'
                            language: 'en'
                        }
                    },
                    {
                        table: 'sys_element_mapping'
                        id: 'e1ea8017c89c49d4ab8f9e97851fef42'
                        deleted: true
                        key: {
                            id: '5e58e21c02d341ae97f3976afbd88d7e'
                            table: 'var__m_sys_hub_step_ext_input_5e58e21c02d341ae97f3976afbd88d7e'
                            field: 'text'
                        }
                    },
                    {
                        table: 'sys_hub_step_ext_output'
                        id: 'e620bfd3fecb4106958e826d52804ad3'
                        deleted: true
                        key: {
                            model: '5e58e21c02d341ae97f3976afbd88d7e'
                            element: 'reversed'
                        }
                    },
                ]
            }
        }
    }
}
