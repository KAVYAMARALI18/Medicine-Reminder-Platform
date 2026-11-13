import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


OPENFDA_LABELS_URL = 'https://api.fda.gov/drug/label.json'
OPENFDA_SOURCE_URL = 'https://open.fda.gov/apis/drug/label/'


class MedicineLookupError(Exception):
    pass


def _label_text(label, field):
    values = label.get(field) or []
    if isinstance(values, str):
        values = [values]
    return '\n\n'.join(str(value) for value in values)[:5000]


def lookup_medicine_information(query):
    term = query.strip()
    if not term or len(term) > 100:
        raise ValueError('Enter a medicine name of 1 to 100 characters.')

    escaped_term = term.replace('\\', '\\\\').replace('"', '\\"')
    search = (
        f'openfda.brand_name:"{escaped_term}" OR '
        f'openfda.generic_name:"{escaped_term}"'
    )
    url = f'{OPENFDA_LABELS_URL}?{urlencode({"search": search, "limit": 1})}'

    try:
        with urlopen(url, timeout=10) as response:
            payload = json.loads(response.read())
    except HTTPError as error:
        if error.code == 404:
            return []
        raise MedicineLookupError('The FDA label service returned an error. Please try again later.') from error
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        raise MedicineLookupError('The FDA label service is unavailable. Please try again later.') from error

    medicines = []
    for label in payload.get('results', []):
        identifiers = label.get('openfda', {})
        brand_names = identifiers.get('brand_name') or []
        generic_names = identifiers.get('generic_name') or []
        product_types = identifiers.get('product_type') or []
        set_ids = identifiers.get('spl_set_id') or []
        source_url = OPENFDA_SOURCE_URL
        if set_ids:
            source_url = (
                'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?'
                + urlencode({'setid': set_ids[0]})
            )
        medicines.append({
            'name': (brand_names or generic_names or [term])[0],
            'generic_name': ', '.join(generic_names),
            'prescription_status': ', '.join(product_types) or 'Not stated in this FDA label',
            'purpose': _label_text(label, 'purpose'),
            'indications': _label_text(label, 'indications_and_usage'),
            'warnings': _label_text(label, 'warnings'),
            'do_not_use': _label_text(label, 'do_not_use'),
            'ask_doctor': _label_text(label, 'ask_doctor')
            or _label_text(label, 'ask_doctor_or_pharmacist'),
            'stop_use': _label_text(label, 'stop_use'),
            'pregnancy': _label_text(label, 'pregnancy_or_breast_feeding'),
            'source_name': 'U.S. FDA openFDA drug product labeling',
            'source_url': source_url,
        })
    return medicines
