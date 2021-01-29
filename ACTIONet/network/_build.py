from typing import Optional, Union
from anndata import AnnData
import numpy as np
from scipy import sparse

import _ACTIONet as _an


def build_network(
        data: Union[AnnData, np.ndarray, sparse.spmatrix],
        net_name_out: Optional[str] = "ACTIONet",
        density: Optional[float] = 1.0,
        thread_no: Optional[int] = 0,
        mutual_edges_only: Optional[bool] = True,
        copy: Optional[bool] = False,
        return_raw: Optional[bool] = False
) -> Union[AnnData, sparse.spmatrix, None]:
    """\
    Build ACTIIONet

    Computes and returns the ACTIONet graph
    Parameters
    ----------
    data
       `n_obs` × `n_arch` Matrix or AnnData object containing output of the 'ACTIONet.prune_archetypes()'.
    net_name_out
        If 'data' is AnnData, store output matrix G in '.obsp' with key 'net_name_out' (default="ACTIONet")
    density
        Controls the overall density of constructed network.
        Larger values results in more retained edges.
    thread_no
        Number of parallel threads used for identifying nearest-neighbors.
        Defaults to available threads on the machine.
    mutual_edges_only
        Whether to return only edges that there is a bi-directional/mutual relationship.
    copy
        If 'data' is AnnData, return a copy instead of writing to `data`.
    return_raw
         If 'return_raw=True' and 'data' is AnnData, return sparse adjacency matrix directly.

    Returns
    -------
    adata : anndata.AnnData
        if 'adata' given and `copy=True` returns None or else adds fields to `adata`:

        `.obsp[net_name_out]`

    G : scipy.sparse.spmatrix
        Sparse adjacency matrix encoding ACTIONet if 'return_raw=True'
    """

    data_is_AnnData = isinstance(data, AnnData)

    if data_is_AnnData:
        adata = data.copy() if copy else data
        H_stacked = adata.obsm["H_stacked"]
    else:
        H_stacked = data

    H_stacked = H_stacked.T.astype(dtype=np.float64)
    if sparse.issparse(H_stacked):
        H_stacked = H_stacked.toarray()
        G = _an.build_ACTIONet(H_stacked, density, thread_no, mutual_edges_only)

    if return_raw or not data_is_AnnData:
        return G
    elif data_is_AnnData:
        adata.obsp[net_name_out] = G
        return adata if copy else None


