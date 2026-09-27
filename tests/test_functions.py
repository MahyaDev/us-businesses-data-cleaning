import pandas as pd
import numpy as np
import pytest

from data_cleaner.functions import (
    clean_state_postal_abbr,
    clean_business_type,
    clean_us_city,
    clean_zip_code,
    clean_address,
    clean_business_name,
    validate_zip_state,
    normalize_entity_type
)

@pytest.mark.parametrize(
        "input_val, expected",
        [
            ("CA", "CA"),
            ("ny", "NY"),
            ("NEW YORK", "NY"),
            ("New York", "NY"),
            ("new york", "NY"),
            ("    CA ", "CA")
        ]
)
def test_clean_state_postal_abbr_valid(input_val, expected):
    assert clean_state_postal_abbr(input_val) == expected

@pytest.mark.parametrize(
        "input_val",
        ["DA", "", np.nan, None]
)
def test_clean_state_postal_abbr_invalid(input_val):
    assert pd.isna(clean_state_postal_abbr(input_val))

@pytest.mark.parametrize(
        "input_val",
        ["NY", "CA", "MD"]
)
def test_clean_state_postal_abbr_idempotent(input_val):
    once = clean_state_postal_abbr(input_val)
    twice = clean_state_postal_abbr(once)

    assert once == twice

@pytest.mark.parametrize(
        "input_val, expected",
        [
            ("CORPORATION", "CORPORATION"),
            ("corporation", "CORPORATION"),
            ("  DBA       ", "DBA"),
            ("L.L.C.", "LLC"),
            ("INC.", "INC"),
            ("SOLE    PROPRIETORSHIP", "SOLE PROPRIETORSHIP")
        ]
)
def test_clean_business_type_valid(input_val, expected):
    assert clean_business_type(input_val) == expected

@pytest.mark.parametrize(
        "input_val",
        ["MONOPOLY", "", np.nan, None]
)
def test_clean_business_type_invalid(input_val):
    assert pd.isna(clean_business_type(input_val))

@pytest.mark.parametrize(
        "input_val",
        ["CORPORATION", "LLC", "SOLE PROPRIETORSHIP"]
)
def test_clean_business_type_idempotent(input_val):
    once = clean_business_type(input_val)
    twice = clean_business_type(once)

    assert once == twice

@pytest.mark.parametrize(
        "input_val, expected",
        [
            ("DELTONA LAKE", "DELTONA LAKE"),
            ("deltona lake", "DELTONA LAKE"),
            ("  LOS ANGELES   ", "LOS ANGELES"),
            ("LOS   ANGELES", "LOS ANGELES"),
            ("MT PLEASANT", "MOUNT PLEASANT"),
            ("W PALM BEACH", "WEST PALM BEACH")
        ]
)
def test_clean_us_city_normalization(input_val, expected):
    assert clean_us_city(input_val) == expected

@pytest.mark.parametrize(
        "input_val",
        ["", np.nan, None]
)
def test_clean_us_city_missing(input_val):
    assert pd.isna(clean_us_city(input_val))

@pytest.mark.parametrize(
        "input_val, expected",
        [
            ("FT LAUDERDALE", "FORT LAUDERDALE"),
            ("FT. LAUDERDALE", "FORT LAUDERDALE"),
            ("N MIAMI BEACH", "NORTH MIAMI BEACH"),
            ("UNIVERSITY PL", "UNIVERSITY PLACE"),
            ("ST PETERSBURG", "SAINT PETERSBURG"),
            ("ST. PETERSBURG", "SAINT PETERSBURG"),
            ("SW RANCHES", "SOUTHWEST RANCHES"),
            ("ARLINGTON HTS", "ARLINGTON HEIGHTS"),
            ("ARLINGTON HTS.", "ARLINGTON HEIGHTS"),
            ("CHELTENHAM TWP", "CHELTENHAM TOWNSHIP"),
            ("CHELTENHAM TWP.", "CHELTENHAM TOWNSHIP")
        ]
)
def test_clean_us_city_abbreviations(input_val, expected):
    assert clean_us_city(input_val) == expected

@pytest.mark.parametrize(
        "input_val, expected",
        [
            ("FORT LAUDEDALE", "FORT LAUDERDALE"),
            ("FORT MEYERS", "FORT MYERS"),
            ("KISSIMMEE FLORIDA", "KISSIMMEE"),
            ("INDPLS", "INDIANAPOLIS"),
            ("STONEMOUNTAIN", "STONE MOUNTAIN"),
            ("LEADVILLLE", "LEADVILLE"),
            ("WILMINGTION", "WILMINGTON")
        ]
)
def test_clean_us_city_typos(input_val, expected):
    assert clean_us_city(input_val) == expected

@pytest.mark.parametrize(
        "input_val",
        [
            "FORT LAUDERDALE",
            "NORTH MIAMI BEACH",
            "CHELTENHAM TOWNSHIP"
        ]
)
def test_clean_us_city_idempotent(input_val):
    once = clean_us_city(input_val)
    twice = clean_us_city(once)

    assert once == twice

@pytest.mark.parametrize(
        "input_val, expected",
        [
            (31419.0, "31419"),
            (6770.0, "06770"),
            (31419, "31419"),
            (6770, "06770"),
            ("46220", "46220"),
            ("6770", "06770"),
            ("  06770 ", "06770")
        ]
)
def test_clean_zip_code_valid(input_val, expected):
    assert clean_zip_code(input_val) == expected

@pytest.mark.parametrize(
        "input_val",
        [0, 123, 123456, 31419.7, "", "ABCDE", "12A34", np.nan, None]
)
def test_clean_zip_code_invalid(input_val):
    assert pd.isna(clean_zip_code(input_val))

@pytest.mark.parametrize(
        "input_val",
        ["46220", "06770", "31419"]
)
def test_clean_zip_code_idempotent(input_val):
    once = clean_zip_code(input_val)
    twice = clean_zip_code(once)

    assert once == twice

@pytest.mark.parametrize(
        "input_val, expected",
        [
            ("5901 e. 38th street", "5901 E 38TH ST"),
            ("  786   KENMORE   AVENUE  ", "786 KENMORE AVE"),
            ("130 S BEMISTON SUITE 101", "130 S BEMISTON STE 101"),
            ("123 MAIN STREET APARTMENT 4B", "123 MAIN ST APT 4B")
        ]
)
def test_clean_address_normalization(input_val, expected):
    assert clean_address(input_val) == expected

@pytest.mark.parametrize(
        "input_val, expected",
        [
            ("10100 SANTA MONICA BLVD, # 300", "10100 SANTA MONICA BLVD, #300"),
            ("1280 S. WILLIAMS DRIVE, P.O. BOX 169", "1280 S WILLIAMS DR, PO BOX 169")
        ]
)
def test_clean_address_punctuation(input_val, expected):
    assert clean_address(input_val) == expected

@pytest.mark.parametrize(
        "input_val",
        ["", np.nan, None]
)
def test_clean_address_missing(input_val):
    assert pd.isna(clean_address(input_val))

@pytest.mark.parametrize(
        "input_val",
        [
            "10100 SANTA MONICA BLVD, #300",
            "1280 S WILLIAMS DR, PO BOX 169",
            "130 S BEMISTON STE 101"
        ]
)
def test_clean_address_idempotent(input_val):
    once = clean_address(input_val)
    twice = clean_address(once)

    assert once == twice

@pytest.mark.parametrize(
        "input_val, expected",
        [
            ('"33"    ESTATES, LLC', '"33" ESTATES, LLC'),
            ('"B.Y.G. & M.Y.D." L.L.C.', '"B.Y.G. & M.Y.D." LLC'),
            ("3d machining and fabrication", "3D MACHINING AND FABRICATION")
        ]
)
def test_clean_business_name_normalization(input_val, expected):
    assert clean_business_name(input_val) == expected

@pytest.mark.parametrize(
        "input_val",
        ["", np.nan, None]
)
def test_clean_business_name_missing(input_val):
    assert pd.isna(clean_business_name(input_val))

@pytest.mark.parametrize(
        "input_val, expected",
        [
            ("ACME CORPORATION", "ACME CORP"),
            ("ACME CORP.", "ACME CORP"),
            ("ACME INCORPORATED", "ACME INC"),
            ("ACME I.N.C.", "ACME INC"),
            ("ACME LIMITED PARTNERSHIP", "ACME LP"),
            ("ACME L.P.", "ACME LP"),
            ("ACME LIMITED LIABILITY PARTNERSHIP", "ACME LLP"),
            ("ACME LLP", "ACME LLP"),
            ("ACME L.L.P.", "ACME LLP")
        ]
)
def test_clean_business_name_entity_types(input_val, expected):
    assert clean_business_name(input_val) == expected

@pytest.mark.parametrize(
        "input_val",
        [
            "ACME CORP",
            "ACME INC",
            "ACME LP",
            "ACME LLP",
            '"33" ESTATES, LLC'
        ]
)
def test_clean_business_name_idempotent(input_val):
    once = clean_business_name(input_val)
    twice = clean_business_name(once)

    assert once == twice

def test_validate_zip_state():
    df = pd.DataFrame({
        "zip": ["10001", "90210", "10001", np.nan, "30301"],
        "state": ["NY", "CA", "TX", "NY", None]
    })

    validation_df = pd.DataFrame({
        "ref_zip": ["10001", "90210", "30301"],
        "ref_state": ["NY", "CA", "GA"]
    })

    result = validate_zip_state(
        df=df,
        validation_df=validation_df,
        zip_col="zip",
        state_col="state",
        ref_zip_col="ref_zip",
        ref_state_col="ref_state"
    )

    expected = pd.Series(
        ["valid", "valid", "invalid", "missing", "missing"],
        index=df.index
    )

    pd.testing.assert_series_equal(result, expected)

def test_normalize_entity_type_order():
    assert normalize_entity_type("ACME LIMITED LIABILITY PARTNERSHIP") == "ACME LLP"

    assert normalize_entity_type("ACME LIMITED PARTNERSHIP") == "ACME LP"
