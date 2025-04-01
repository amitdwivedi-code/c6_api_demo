esg_lead_permissions = {
    "Workplace": {
        "Workforce": {
            "Overview": ["add", "edit", "delete", "view"],
            "Employees": ["add", "edit", "delete", "view"],
            "Workers": ["add", "edit", "delete", "view"],
            "Management": ["add", "edit", "delete", "view"],
            "Wages": ["add", "edit", "delete", "view"],
        },
        "Training": {
            "Overview": ["add", "edit", "delete", "view"],
            "Manhours": ["add", "edit", "delete", "view"],
            "Career Development": ["add", "edit", "delete", "view"],
            "Awareness Programmes": ["add", "edit", "delete", "view"],
            "Health And Safety": ["add", "edit", "delete", "view"],
        },
        "Health And Safety": {
            "Overview": ["add", "edit", "delete", "view"],
            "Posh": ["add", "edit", "delete", "view"],
            "WellBeing Measures": ["add", "edit", "delete", "view"],
            "Workplace Safety": ["add", "edit", "delete", "view"],
        },
        "Grievances": {"Grievances": ["add", "edit", "delete", "view"]},
        "Policies and Penalties": {
            "Health And Safety": ["add", "edit", "delete", "view"],
            "Human Rights": ["add", "edit", "delete", "view"],
            "Penalty": ["add", "edit", "delete", "view"],
        },
    },
    "Environment": {
        "Lifecycle": {
            "Material": ["add", "edit", "delete", "view"],
            "Reclaim": ["add", "edit", "delete", "view"],
            "Lifecycle Assesment": ["add", "edit", "delete", "view"],
        },
        "Energy": {
            "Overall": ["add", "edit", "delete", "view"],
            # "Emissions": ["add", "edit", "delete", "view"],
            "Electricity": ["add", "edit", "delete", "view"],
            "Fuel Combustion": ["add", "edit", "delete", "view"],
            "Logistics": ["add", "edit", "delete", "view"],
            "Travel": ["add", "edit", "delete", "view"],
            "Energy Intensity": ["add", "edit", "delete", "view"],
            "Others": ["add", "edit", "delete", "view"],
        },
        "Water and Air": {
            "Overall": ["add", "edit", "delete", "view"],
            "Withdrawal": ["add", "edit", "delete", "view"],
            "Consumption": ["add", "edit", "delete", "view"],
            "Discharge": ["add", "edit", "delete", "view"],
            "Air Emission": ["add", "edit", "delete", "view"],
        },
        "GHG_emission": {
            "Overall": ["add", "edit", "delete", "view"],
            "Scope1": ["add", "edit", "delete", "view"],
            "Scope2": ["add", "edit", "delete", "view"],
            "Scope3": ["add", "edit", "delete", "view"],
        },
        "Waste": {
            "Overall": ["add", "edit", "delete", "view"],
            "Waste Generated": ["add", "edit", "delete", "view"],
            "Recovered": ["add", "edit", "delete", "view"],
            "Disposed": ["add", "edit", "delete", "view"],
        },
        "Sustanibility": {
            "Environmental Impact": ["add", "edit", "delete", "view"],
            "Policies and Projects": ["add", "edit", "delete", "view"],
        },
    },
    "Community": {
        "Community": {
            "Stackholders": ["add", "edit", "delete", "view"],
            "Society": ["add", "edit", "delete", "view"],
            "CSR": ["add", "edit", "delete", "view"],
            "Consumer": ["add", "edit", "delete", "view"],
        }
    },
    "Company Details": {
        "Company Profile": {
            "Company Profile": ["add", "edit", "delete", "view"],
            "Financials": ["add", "edit", "delete", "view"],
            "Bussiness Activity": ["add", "edit", "delete", "view"],
            "Operations": ["add", "edit", "delete", "view"],
        }
    },
    "BRS": {
        "BRS Policy": {
            "Policy and Management Processes": ["add", "edit", "delete", "view"],
            "Governance,Leadership and Oversight": ["add", "edit", "delete", "view"],
        },
        "BRS Report":  {
            "BRS Report": ["view"],
        }        
    },

}

user_permissions = {
    "Workplace": {
        "Workforce": {
            "Overview": [],
            "Employees": [],
            "Workers": [],
            "Management": [],
            "Wages": [],
        },
        "Training": {
            "Overview": [],
            "Manhours": [],
            "Career Development": [],
            "Awareness Programmes": [],
            "Health And Safety": [],
        },
        "Health And Safety": {
            "Overview": [],
            "Posh": [],
            "WellBeing Measures": [],
            "Workplace Safety": [],
        },
        "Grievances": {"Grievances": []},
        "Policies and Penalties": {
            "Health And Safety": [],
            "Human Rights": [],
            "Penalty": [],
        },
    },
    "Environment": {
        "Lifecycle": {
            "Material": [],
            "Reclaim": [],
            "Lifecycle Assesment": [],
        },
        "Energy": {
            "Overall": [],
            # "Emissions": [],
            "Electricity": [],
            "Fuel Combustion": [],
            "Logistics": [],
            "Travel": [],
            "Energy Intensity": [],
            "Others": [],
        },
        "Water and Air": {
            "Overall": [],
            "Withdrawal": [],
            "Consumption": [],
            "Discharge": [],
            "Air Emission": [],
        },
        "GHG_emission": {
            "Overall": [],
            "Scope1": [],
            "Scope2": [],
            "Scope3": [],
        },
        "Waste": {
            "Overall": [],
            "Waste Generated": [],
            "Recovered": [],
            "Disposed": [],
        },
        "Sustanibility": {
            "Environmental Impact": [],
            "Policies and Projects": [],
        },
    },
    "Community": {
        "Community": {
            "Stackholders": [],
            "Society": [],
            "CSR": [],
            "Consumer": [],
        }
    },
    "Company Details": {
        "Company Profile": {
            "Company Profile": [],
            "Financials": [],
            "Bussiness Activity": [],
            "Operations": [],
        }
    },
    "BRS": {
        "BRS Policy": {
            "Policy and Management Processes": [],
            "Governance,Leadership and Oversight": [],
        },
        "BRS Report":  {
            "BRS Report": [],
        }   
    },
}



role_wise_permissions = {

        "Finance": {
            "Company Details": {
                "Company Profile": {
                    "Company Profile": ["view"],
                    "Financials": ["add", "edit", "delete", "view"],
                    "Bussiness Activity": ["view"],
                    "Operations": ["view"],
                }
            }
    },





        "Human Resource": {
            "Company Details": {
                "Company Profile": {
                    "Company Profile": ["view"],
                    "Bussiness Activity": ["view"],
                    "Operations": ["view"],
                }
            },

            "Workplace": {
                "Workforce": {
                    "Overview": ["add", "edit", "delete", "view"],
                    "Employees": ["add", "edit", "delete", "view"],
                    "Workers": ["add", "edit", "delete", "view"],
                    "Management": ["add", "edit", "delete", "view"],
                    "Wages": ["add", "edit", "delete", "view"],
                },
                "Training": {
                    "Overview": ["add", "edit", "delete", "view"],
                    "Manhours": ["add", "edit", "delete", "view"],
                    "Career Development": ["add", "edit", "delete", "view"],
                    "Awareness Programmes": ["add", "edit", "delete", "view"],
                    "Health And Safety": ["add", "edit", "delete", "view"],
                },
                "Health And Safety": {
                    "Overview": ["add", "edit", "delete", "view"],
                    "Posh": ["add", "edit", "delete", "view"],
                    "WellBeing Measures": ["add", "edit", "delete", "view"],
                    "Workplace Safety": ["add", "edit", "delete", "view"],
                },
                "Grievances": {"Grievances": ["add", "edit", "delete", "view"]},
                "Policies and Penalties": {
                    "Health And Safety": ["add", "edit", "delete", "view"],
                    "Human Rights": ["add", "edit", "delete", "view"],
                    "Penalty": ["add", "edit", "delete", "view"],
                },
            },
    },





        "Company Secretary": {
            "Company Details": {
                "Company Profile": {
                    "Company Profile": ["view"],
                    "Bussiness Activity": ["view"],
                    "Operations": ["view"],
                }
            },

        "Community": {
            "Community": {
                "Stackholders": ["add", "edit", "delete", "view"],
                # "Society": ["add", "edit", "delete", "view"],
                # "CSR": ["add", "edit", "delete", "view"],
                # "Consumer": ["add", "edit", "delete", "view"],
            }
        },

        "BRS": {
            "BRS Policy": {
                "Policy and Management Processes": ["add", "edit", "delete", "view"],
                "Governance,Leadership and Oversight": ["add", "edit", "delete", "view"],
            },
            "BRS Report":  {
                "BRS Report": ["view"],
            }   
        },
    },





        "Plant Operations" : {
            "Company Details": {
                "Company Profile": {
                    "Company Profile": ["view"],
                }
            },

        "Environment": {
            "Energy": {
                "Overall": ["view"],
                # "Emissions": ["add", "edit", "delete", "view"],
                "Electricity": ["add", "edit", "delete", "view"],
                "Fuel Combustion": ["add", "edit", "delete", "view"],
                "Logistics": ["add", "edit", "delete", "view"],
                "Energy Intensity": ["view"],
                "Travel": ["add", "edit", "delete", "view"],
                "Others" : ["add", "edit", "delete", "view"],
            },
            "Water and Air": {
                "Overall": ["view"],
                "Withdrawal": ["add", "edit", "delete", "view"],
                "Consumption": ["add", "edit", "delete", "view"],
                "Discharge": ["add", "edit", "delete", "view"],
                "Air Emission": ["add", "edit", "delete", "view"],
            },
            "GHG_emission": {
                "Overall": ["view"],
                # "Scope1": ["view"],
                # "Scope2": ["view"],
                # "Scope3": ["view"],
            },
            "Waste": {
                "Overall": ["view"],
                "Waste Generated": ["add", "edit", "delete", "view"],
                "Recovered": ["add", "edit", "delete", "view"],
                "Disposed": ["add", "edit", "delete", "view"],
            },
            "Sustanibility": {
                "Environmental Impact": ["view"],
                "Policies and Projects": ["view"],
            },
        },
    }

}