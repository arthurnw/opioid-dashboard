# CDC Wonder Parameters

## Group By


## Filters

### States
State filter parameters must be passed into **two** form data entries:

* `F_D77.V9`
* `I_D77.V9`

For example, these are the entries to filter down to Alabama:

```
'F_D77.V9': '01',
'I_D77.V9': '01 (Alabama)'
```

The file `state_codes_V_D77.V9` has two columns, each of which corresponds to one of the form data entries:

| Column Name | Form Data Entry |
|---|---|
| Code | F_D77.V9 |
| Label | I_D77.V9 |

## Counties
County filter parameters must be passed into **two** form data entries:

* `F_D77.V9`
* `I_D77.V9`

For example, these are the entries to filter down to Autauga County, AL:

```
'F_D77.V9': '01001'
'I_D77.V9': '01001 (Autauga County, AL)'
```

The file `counties_D77.V9.csv` contains codes and labels for counties.

### Age Groups
If filtering by ten-year age groups, `O_age` should have a value of `D77.V5`:

```
'O_age': 'D77.V5'
```

And the selected age group should be set in `V_D77.V5`:

```
'V_D77.V5': '1-4'
```

If multiple age groups are selected, pass them in as a list:

```
'V_D77.V5': ['1', '1-4', '5-14', '15-24', '25-34', '35-44']
```

See [this link](https://stackoverflow.com/questions/23384230/how-to-post-multiple-value-with-same-key-in-python-requests) for another example.

The file `age_groups_D77.V5.csv` contains codes and labels.

### Years
Year filter parameters must be passed into **two** form data entries:

* `F_D77.V1`
* `I_D77.V1`

For example, these are the entries to filter down to 2015:

```
'F_D77.V1': '2015',
'I_D77.V1': '2015 (2015)'
```

The options for the data entries can be found in the files:

* `years_F_D77.V1.csv`
* `years_I_D77.V1.csv`

The file `years_I_D77.V1.csv` contains the codes and labels for each year.

### Underlying Cause of Death
Underlying cause of death filter parameters must be passed into **two** form data entries:

* `F_D77.V2` (just the code)
* `I_D77.V2` (code and label)

For example, these are the entries to filter down to X40:

```
'F_D77.V2': 'X40',
'I_D77.V2': 'X40 (Accidental poisoning by and exposure to nonopioid analgesics, antipyretics and antirheumatics)'
```

If multiple underlying causes of death are selected, pass them in as a list:

```
'F_D77.V2': ['X40', 'X41', 'X42', 'X43', 'X44', 'X60', 'X61', 'X62', 'X63', 'X64', 'X85', 'Y10', 'Y11', 'Y12', 'Y13', 'Y14'],
'I_D77.V2': [
	'X40 (Accidental poisoning by and exposure to nonopioid analgesics, antipyretics and antirheumatics)'
	'X41 (Accidental poisoning by and exposure to antiepileptic, sedative-hypnotic, antiparkinsonism and psychotropic drugs, not elsewhere classified)',
	'X42 (Accidental poisoning by and exposure to narcotics and psychodysleptics [hallucinogens], not elsewhere classified)',
	'X43 (Accidental poisoning by and exposure to other drugs acting on the autonomic nervous system)',
	'X44 (Accidental poisoning by and exposure to other and unspecified drugs, medicaments and biological substances)',
	'X60 (Intentional self-poisoning by and exposure to nonopioid analgesics, antipyretics and antirheumatics)',
	'X61 (Intentional self-poisoning by and exposure to antiepileptic, sedative-hypnotic, antiparkinsonism and psychotropic drugs, not elsewhere classified)',
	'X62 (Intentional self-poisoning by and exposure to narcotics and psychodysleptics [hallucinogens], not elsewhere classified)',
	'X63 (Intentional self-poisoning by and exposure to other drugs acting on the autonomic nervous system)',
	'X64 (Intentional self-poisoning by and exposure to other and unspecified drugs, medicaments and biological substances)',
	'X85 (Assault by drugs, medicaments and biological substances)',
	'Y10 (Poisoning by and exposure to nonopioid analgesics, antipyretics and antirheumatics, undetermined intent)',
	'Y11 (Poisoning by and exposure to antiepileptic, sedative-hypnotic, antiparkinsonism and psychotropic drugs, not elsewhere classified, undetermined intent)',
	'Y12 (Poisoning by and exposure to narcotics and psychodysleptics [hallucinogens], not elsewhere classified, undetermined intent)',
	'Y13 (Poisoning by and exposure to other drugs acting on the autonomic nervous system, undetermined intent)',
	'Y14 (Poisoning by and exposure to other and unspecified drugs, medicaments and biological substances, undetermined intent)'
	]
```

The file `ucd_D77.V2.csv` contains the top-level code and label values that can be passed in. The examples above are filtered down to opioid-related deaths, per the methodology used at http://drugabuse.gov. Those values are at a lower level not accessible in the page source.

### Multiple Cause of Death
Multiple cause of death filter parameters must be passed in to **two** form data entries:

* `F_D77.V13` (just the code)
* `V_D77.V13` (code and label)

For example, these are the entries to filter down to T40.1:

```
'V_D77.V13': 'T40.1 (Heroin)',
'F_D77.V13': 'T40.1'
```

If multiple contributing causes are selected, pass them in as a list:

```
'V_D77.V13': [
	'T40.1 (Heroin)',
	'T40.2 (Other opioids),'
	'T40.3 (Methadone)',
	'T40.4 (Other synthetic narcotics)',
	'T40.6 (Other and unspecified narcotics)'
	],
'F_D77.V13': ['T40.1', 'T40.2', 'T40.3', 'T40.4', 'T40.6']
```

The file `mcd_D77.V13.csv` contains the top-level code and label valus that can be passed in. The examples above are filtered down to opioid-related deaths, per the methodology used at http://drugabuse.gov. Those values are at a lower level not accessible in the page source.


# Ancillary

## Demographic Data

### Generate input files for data_harmonizer.py

1. Unzip the 2003 demographic zip into a folder
2. cd into that directory
3. head -n1 demographics_2003_st01.csv > ../demographics_2003.csv
4. for X in *.csv; do echo $X; tail -n+2 $X >> ../demographics_2003.csv; done
5. cd ../
6. head -n 3000001 demographics_2003.csv > demographics_2003a.csv
7. head -n 1 demographics_2003.csv > demographics_2003b.csv
8. tail -n+3000002 demographics_2003.csv >> demographics_2003b.csv
9. Move a and b files to data_raw