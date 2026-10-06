# Survey comparison

The surveys supported by MobiSurvStd measure the same concepts (transportation modes, trip purposes,
education levels, etc.) but each survey type uses its own definitions and its own lists of codes.
MobiSurvStd maps all of them to a single set of modalities, which means that some information is
merged or lost along the way.

The pages in this section show how the surveys differ and how they are mapped:

- [Availability table](./table.md): share of non-NULL values of each variable, for each survey type
- [Modes](./modes.md): original transportation modes mapped to each MobiSurvStd mode
- [Purposes](./purposes.md): original trip purposes mapped to each MobiSurvStd purpose
- [Education levels](./education.md): original education levels mapped to each MobiSurvStd
  education level
- [Professional occupations](./occupation.md): original professional occupations mapped to each
  MobiSurvStd professional occupation

## How to read the comparison tables

In the mode, purpose, education-level, and professional-occupation tables:

- Each row is a MobiSurvStd modality and each column is a survey type.
- Each cell lists the original modalities mapped to that MobiSurvStd modality, as `code` followed by
  the label from the survey's documentation (in French).
  When several original modalities are mapped to the same MobiSurvStd modality, they are listed on
  separate lines.
- A dash (–) means that the survey type has no modality mapped to that MobiSurvStd modality.
- The EMC², EDGT, EDVM, and EMD surveys share a single column when they use the same definitions.
- The Nantes open-data survey is not shown.

The notes below each table describe the special cases which cannot be read from the table (e.g.,
values that are corrected based on other variables).
