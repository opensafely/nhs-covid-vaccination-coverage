from cohortextractor import (
    codelist,
    codelist_from_csv,
)

care_home_snomed_codes = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-longres.csv", system="snomed", column="code")

high_risk_codes = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-shield.csv", system="snomed", column="code")

not_high_risk_codes = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-nonshield.csv", system="snomed", column="code")

adrenaline_pen = codelist_from_csv(
    "codelists/opensafely-adrenaline-pens.csv", system="snomed", column="dmd_id"
)

chronic_cardiac_disease_codes = codelist_from_csv(
    "codelists/opensafely-chronic-cardiac-disease.csv", system="ctv3", column="CTV3ID",
)

chemotherapy_or_radiotherapy_codes = codelist_from_csv(
    "codelists/opensafely-chemotherapy-or-radiotherapy.csv",
    system="ctv3",
    column="CTV3ID",
)
cancer_excluding_lung_and_haematological_codes = codelist_from_csv(
    "codelists/opensafely-cancer-excluding-lung-and-haematological.csv",
    system="ctv3",
    column="CTV3ID",
)

covid_primary_care_positive_test = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-probable-covid-positive-test.csv",
    system="ctv3",
    column="CTV3ID",
)

covid_primary_care_code = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-probable-covid-clinical-code.csv",
    system="ctv3",
    column="CTV3ID",
)

covid_primary_care_sequalae = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-probable-covid-sequelae.csv",
    system="ctv3",
    column="CTV3ID",
)

current_copd_codes = codelist_from_csv(
    "codelists/opensafely-current-copd.csv", system="ctv3", column="CTV3ID"
)

dementia_codes = codelist_from_csv(
    "codelists/opensafely-dementia-complete.csv", system="ctv3", column="code"
)

dmards_codes = codelist_from_csv(
    "codelists/opensafely-dmards.csv", system="snomed", column="snomed_id",
)

dialysis_codes = codelist_from_csv(
    "codelists/opensafely-dialysis.csv", system="ctv3", column="CTV3ID",
)

ethnicity_codes = codelist_from_csv(
    "codelists/opensafely-ethnicity.csv",
    system="ctv3",
    column="Code",
    category_column="Grouping_6",
)
ethnicity_codes_16 = codelist_from_csv(
    "codelists/opensafely-ethnicity.csv",
    system="ctv3",
    column="Code",
    category_column="Grouping_16",
)


solid_organ_transplantation_codes = codelist_from_csv(
    "codelists/opensafely-solid-organ-transplantation.csv",
    system="ctv3",
    column="CTV3ID",
)

lung_cancer_codes = codelist_from_csv(
    "codelists/opensafely-lung-cancer.csv", system="ctv3", column="CTV3ID",
)
haematological_cancer_codes = codelist_from_csv(
    "codelists/opensafely-haematological-cancer.csv", system="ctv3", column="CTV3ID",
)
bone_marrow_transplant_codes = codelist_from_csv(
    "codelists/opensafely-bone-marrow-transplant.csv", system="ctv3", column="CTV3ID",
)
cystic_fibrosis_codes = codelist_from_csv(
    "codelists/opensafely-cystic-fibrosis.csv", system="ctv3", column="CTV3ID",
)

sickle_cell_disease_codes = codelist_from_csv(
    "codelists/opensafely-sickle-cell-disease.csv", system="ctv3", column="CTV3ID",
)

ssri_codes = codelist_from_csv(
    "codelists/opensafely-selective-serotonin-reuptake-inhibitors-dmd.csv",
    system="snomed",
    column="dmd_id",
)


permanent_immunosuppression_codes = codelist_from_csv(
    "codelists/opensafely-permanent-immunosuppression.csv",
    system="ctv3",
    column="CTV3ID",
)

temporary_immunosuppression_codes = codelist_from_csv(
    "codelists/opensafely-temporary-immunosuppression.csv",
    system="ctv3",
    column="CTV3ID",
)

chronic_cardiac_disease_codes = codelist_from_csv(
    "codelists/opensafely-chronic-cardiac-disease.csv", system="ctv3", column="CTV3ID",
)

intellectual_disability_including_downs_syndrome_codes = codelist_from_csv(
    "codelists/opensafely-intellectual-disability-including-downs-syndrome.csv",
    system="ctv3",
    column="CTV3ID",
)
dialysis_codes = codelist_from_csv(
    "codelists/opensafely-dialysis.csv", system="ctv3", column="CTV3ID",
)

other_respiratory_conditions_codes = codelist_from_csv(
    "codelists/opensafely-other-respiratory-conditions.csv",
    system="ctv3",
    column="CTV3ID",
)

heart_failure_codes = codelist_from_csv(
    "codelists/opensafely-heart-failure.csv", system="ctv3", column="CTV3ID",
)

other_heart_disease_codes = codelist_from_csv(
    "codelists/opensafely-other-heart-disease.csv", system="ctv3", column="CTV3ID",
)

chronic_liver_disease_codes = codelist_from_csv(
    "codelists/opensafely-chronic-liver-disease.csv", system="ctv3", column="CTV3ID",
)

other_neuro_codes = codelist_from_csv(
    "codelists/opensafely-other-neurological-conditions.csv",
    system="ctv3",
    column="CTV3ID",
)

psychosis_schizophrenia_bipolar_affective_disease_codes = codelist_from_csv(
    "codelists/opensafely-psychosis-schizophrenia-bipolar-affective-disease.csv",
    system="ctv3",
    column="CTV3Code",
)

asplenia_codes = codelist_from_csv(
    "codelists/opensafely-asplenia.csv", system="ctv3", column="CTV3ID"
)

wider_ld_codes = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-learndis.csv", system="snomed", column="code"
)

covid_vacc_declined = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-cov1decl.csv", system="snomed", column="code"
)

housebound_codes = codelist_from_csv(
    "codelists/opensafely-housebound.csv", system="snomed", column="code"
)

no_longer_housebound_codes = codelist_from_csv(
    "codelists/opensafely-no-longer-housebound.csv", system="snomed", column="code"
)

# Chronic kidney disease diagnostic codes
ckd_cov = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-ckd_cov.csv", system="snomed", column="code"
)

# Chronic kidney disease codes - all stages
ckd15 = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-ckd15.csv", system="snomed", column="code"
)

# Chronic kidney disease codes-stages 3 - 5
ckd35 = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-ckd35.csv", system="snomed", column="code"
)

### Immune-mediated inflammatory diseases (IMID), as used here:
### https://www.medrxiv.org/content/10.1101/2021.09.03.21262888v1

# CLINICAL CONDITIONS CODELISTS
crohns_disease_codes = codelist_from_csv(
    "codelists/opensafely-crohns-disease.csv", system="ctv3", column="code",
)

ulcerative_colitis_codes = codelist_from_csv(
    "codelists/opensafely-ulcerative-colitis.csv", system="ctv3", column="code",
)

inflammatory_bowel_disease_unclassified_codes = codelist_from_csv(
    "codelists/opensafely-inflammatory-bowel-disease-unclassified.csv", system="ctv3", column="code",
)

ankylosing_spondylitis_codes = codelist_from_csv(
    "codelists/user-mark-yates-axial-spondyloarthritis.csv", system="snomed", column="code",
)

psoriasis_codes = codelist_from_csv(
    "codelists/opensafely-psoriasis.csv", system="ctv3", column="code",
)

hidradenitis_suppurativa_codes = codelist_from_csv(
    "codelists/opensafely-hidradenitis-suppurativa.csv", system="ctv3", column="CTV3ID",
)

psoriatic_arthritis_codes = codelist_from_csv(
    "codelists/opensafely-psoriatic-arthritis.csv", system="snomed", column="id",
)

rheumatoid_arthritis_codes = codelist_from_csv(
    "codelists/opensafely-rheumatoid-arthritis.csv", system="ctv3", column="CTV3ID",
)

### Adding relevant PRIMIS codes to generate at risk group
immdx_cov_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-immdx_cov.csv",
    system="snomed",
    column="code",
)

immrx_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-immrx.csv",
    system="snomed",
    column="code",
)

dxt_chemo_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-dxt_chemo_cod.csv",
    system="snomed",
    column="code",
)

ckd_cov_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-ckd_cov.csv",
    system="snomed",
    column="code",
)

ckd15_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-ckd15.csv",
    system="snomed",
    column="code",
)

ckd35_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-ckd35.csv",
    system="snomed",
    column="code",
)

astadm_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-astadm.csv",
    system="snomed",
    column="code",
)

ast_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-ast.csv",
    system="snomed",
    column="code",
)

astrxm1_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-astrxm1.csv",
    system="snomed",
    column="code",
)

astrxm2_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-astrxm2.csv",
    system="snomed",
    column="code",
)

resp_cov_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-resp_cov.csv",
    system="snomed",
    column="code",
)

diab_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-diab.csv",
    system="snomed",
    column="code",
)

dmres_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-dmres.csv",
    system="snomed",
    column="code",
)

addis_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-addis_cod.csv",
    system="snomed",
    column="code",
)
gdiab_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-gdiab_cod.csv",
    system="snomed",
    column="code",
)

preg_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-preg.csv",
    system="snomed",
    column="code",
)

pregdel_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-pregdel.csv",
    system="snomed",
    column="code",
)

cld_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-cld.csv",
    system="snomed",
    column="code",
)

cns_cov_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-cns_cov.csv",
    system="snomed",
    column="code",
)

chd_cov_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-chd_cov.csv",
    system="snomed",
    column="code",
)

spln_cov_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-spln_cov.csv",
    system="snomed",
    column="code",
)

learndis_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-learndis.csv",
    system="snomed",
    column="code",
)

sev_mental_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-sev_mental.csv",
    system="snomed",
    column="code",
)

smhres_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-smhres.csv",
    system="snomed",
    column="code",
)

hhld_imdef_cod=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-hhld_imdef.csv",
    system="snomed",
    column="code",
) 
