import pandas as pd
import numpy as np
import re
from .constants import (
    US_STATES_POSTAL_ABBR,
    VALID_BUSINESS_TYPES,
    STREET_SUFFIX_ABBR,
    SECONDARY_UNIT_DESIGNATORS,
    ENTITY_TYPES
)

def clean_state_postal_abbr(value: str | None) -> str:
    if pd.isna(value):
        return np.nan

    value = str(value).upper().strip()

    if value in US_STATES_POSTAL_ABBR.keys():
        return value

    elif value in US_STATES_POSTAL_ABBR.values():
        for abbr, state_name in US_STATES_POSTAL_ABBR.items():
            if state_name.upper() == value:
                return abbr

    return np.nan

def clean_business_type(value: str | None) -> str:
    if pd.isna(value):
        return np.nan

    value = str(value).upper().strip()

    value = re.sub(r'\s*\.\s*', '', value)

    if value in VALID_BUSINESS_TYPES:
        return value

    return np.nan

def clean_us_city(value: str | None) -> str:
    if pd.isna(value):
        return np.nan

    value = str(value).strip().upper()

    value = re.sub(r'\s+', ' ', value)

    value = re.sub(r'^[^a-zA-Z]+|[^a-zA-Z]+$', '', value)

    value = re.sub(r'\s*\.\s*', '. ', value)

    abbreviation_map = {
        'FT': 'FORT',
        'FT.': 'FORT',
        'MT': 'MOUNT',
        'MT.': 'MOUNT',
        'N': 'NORTH',
        'PL': 'PLACE',
        'ST': 'SAINT',
        'ST.': 'SAINT',
        'SW': 'SOUTHWEST',
        'W': 'WEST',
        'HTS': 'HEIGHTS',
        'HTS.': 'HEIGHTS',
        'TWP': 'TOWNSHIP',
        'TWP.': 'TOWNSHIP'
    }

    words = value.split(' ')
    expanded_words = []

    for word in words:
        if word in abbreviation_map:
            expanded_words.append(abbreviation_map[word])
        else:
            expanded_words.append(word)

    value = ' '.join(expanded_words)

    typo_map = {
        'FORT LAUDEDALE': 'FORT LAUDERDALE',
        'FORT MEYERS': 'FORT MYERS',
        'KISSIMMEE FLORIDA': 'KISSIMMEE',
        'INDPLS': 'INDIANAPOLIS',
        'STONEMOUNTAIN': 'STONE MOUNTAIN',
        'LEADVILLLE': 'LEADVILLE',
        'WILMINGTION': 'WILMINGTON'
    }

    if value in typo_map:
        value = typo_map[value]

    return value

def clean_zip_code(zip_code: float | int | None) -> str | float:
    if pd.isna(zip_code):
        return np.nan

    if zip_code == 0:
        return np.nan

    zip_code = str(int(zip_code))

    if len(zip_code) == 4:
        zip_code = zip_code.zfill(5)
        return zip_code

    if len(zip_code) == 5:
        return zip_code

    return np.nan

def validate_zip_state(
    df: pd.DataFrame,
    validation_df: pd.DataFrame,
    zip_col: str,
    state_col: str,
    ref_zip_col: str,
    ref_state_col: str
) -> pd.Series:

    df_copy = df[
        [zip_col, state_col]
    ].copy()

    validation_ref = validation_df[
        [ref_zip_col, ref_state_col]
    ].copy()

    df_copy[zip_col] = df_copy[zip_col].astype("string").str[:2]

    validation_ref[ref_zip_col] = validation_ref[ref_zip_col].astype("string").str[:2]

    validation_ref = validation_ref.drop_duplicates()

    valid_combinations = pd.MultiIndex.from_frame(
        validation_ref[[ref_zip_col, ref_state_col]]
    )

    df_combinations = pd.MultiIndex.from_frame(
        df_copy[[zip_col, state_col]]
    )

    result = pd.Series("invalid", index=df.index)

    missing = (df_copy[zip_col].isna() | df_copy[state_col].isna())

    valid = df_combinations.isin(valid_combinations)

    result[missing] = "missing"
    result[valid & ~missing] = "valid"

    return result

def clean_address(value):
    if pd.isna(value):
        return np.nan

    value = str(value).upper()

    value = re.sub(r'\s*\,\s*', ', ', value)

    value = re.sub(r'\s*#\s*(\d+)', r' #\1', value)

    value = re.sub(r'\.', '', value)

    value = re.sub(r'\s+', ' ', value)

    value = value.strip()

    words = value.split(' ')
    expanded_words = []

    for word in words:
        if word in STREET_SUFFIX_ABBR:
            expanded_words.append(STREET_SUFFIX_ABBR[word])
        elif word in SECONDARY_UNIT_DESIGNATORS:
            expanded_words.append(SECONDARY_UNIT_DESIGNATORS[word])
        else:
            expanded_words.append(word)

    value = ' '.join(expanded_words)

    return value

def normalize_entity_type(value):
    if pd.isna(value):
        return np.nan

    value = str(value).strip().upper()

    for pattern, replacement in ENTITY_TYPES.items():
        value = re.sub(pattern, replacement, value)

    return value

def clean_business_name(value):
    if pd.isna(value):
        return np.nan

    value = str(value).strip().upper()

    value = re.sub(r'\s+', ' ', value)

    value = normalize_entity_type(value)

    return value
