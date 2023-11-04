"""
utils.py
"""

from typing import Any, Dict, Optional
import pylcs

def merge_dict(dict1 : Dict[Any, Any],
               dict2: Dict[Any, Any],
               merge_values: Optional[bool] = True,
               ) -> Dict[Any, Any]:
    """Merge two dictionnaries together

    Parameters
    ----------

    dict1 : dict
        first dict to merge
    dict2 : dict
        second dict to merge
    merge_values : bool
        if True value of same keys in both dicts are concateneted into a list
        if False, value in the first dict are replaced with the ones in the second
        dict

    Returns
    -------
    dict :
        merged dict
    """
    if dict1 is None:
        dict1 = {}
    if dict2 is None:
        dict2 = {}
    merged_dict = {**dict1, **dict2}
    if merge_values:
        for key in set(dict1.keys() & dict2.keys()):
            merged_dict[key] = [merged_dict[key], dict2[key]]
    return merged_dict


def flatten_dict(nested_dict : Dict[str, Any],
                 sep : Optional[str] = '/',
                 parent_key : Optional[str | None] = None
                 ) -> Dict[str, Any]:
    """Return a flattened version of the input dict

    Parameters
    ----------
    dict : dict
        nested dict to be flattened
    sep : str, optional
        separator to add between keys in flattened dict
    parent_key : str, optional
        parent key name to add before all `nested_dict` keys

    Returns
    -------
    dict:
        flattened dict
    """
    flattened = {}
    for key, value in nested_dict.items():
        if parent_key is None:
            new_key = key
        else:
            new_key = f"{parent_key}{sep}{key}"
        if isinstance(value, dict):
            flattened.update(flatten_dict(value, sep=sep, parent_key=new_key))
        elif isinstance(value, list):
            # here we suppose that the type of elements is homogeneous on the list
            # and we only flatten dict
            if len(value) > 0 and isinstance(value[0], dict):
                # flatten each dict in the list
                for idx, current_dict in enumerate(value):
                    updated_key = f"{new_key}{sep}{idx}"
                    flattened.update(flatten_dict(current_dict, sep=sep, parent_key=updated_key))
            else:
                flattened[new_key] = value
        else:
            flattened[new_key] = value
    return flattened


def get_best_items(input_dict : Dict[str, Any],
                   target : str,
                   tolerance : Optional[float] =0.
                   )-> dict[str, Any]:
    """Return a subdict containing couples key/value that best match the
    specified target key

    Parameters
    ----------
    d : dict
        dictionnary in which search best correspondances
    target: str
        target key to search in the dictionnary
    tolerance: float, optional
        tolerance applied on items score. Default to 0

    Returns
    -------
    dict:
        a dictionnary containing the key that have matched with the target key,
        and corresponding values.
    """
    # compute the normalized longest common subsequence score for each key in the input dict
    lcs_scores = [pylcs.lcs(key, target) / len(target) for key in input_dict]
    # compute the normalized Levenshtein distance for each key in the input dict
    lev_dists = [pylcs.levenshtein_distance(key, target) / max(len(key), len(target))
                 for key in input_dict]
    # The following calculation is used to penalize the score obtained for the lcs,
    # taking into account deletions and insertions relative to the target in each key
    scores = [(key, lcs_scores[i] - lev_dists[i]) for i, key in enumerate(input_dict)]
    best_score = max(scores, key=lambda x : x[1])[1]
    # keep only keys with best score (taking into account a tolerance)
    filtered_keys = [score[0] for score in scores if score[1] >= best_score - tolerance]
    filtered_dict = {key : value for key, value in input_dict.items() if key in filtered_keys}

    return filtered_dict

