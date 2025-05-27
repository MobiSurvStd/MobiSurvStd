from . import egt2020

# def emc2_import(input_directory: str, output_directory: str):
#     survey_data = emc2.standardize(input_directory)
#     survey_data = survey_data.clean()
#     survey_data.save(output_directory)


def egt2020_import(input_directory: str, output_directory: str):
    survey_data = egt2020.standardize(input_directory)
    # survey_data = survey_data.clean()
    survey_data.save(output_directory)
