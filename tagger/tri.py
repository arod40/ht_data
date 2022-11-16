from math import floor, sqrt


class TriL:
    def __init__(self, diag=False):
        self.diag = diag

    # O(1) solution to convert i,j into flatten indices of the lower triangular matrix
    def _tril_ij_to_idx(self, i, j, diag=False):
        if not diag:
            i -= 1
        if i < 0 or i > j:
            raise Exception("Wrong indices for lower triangular matrix!")
        return i * (i - 1) / 2 + j

    # O(1) solution to convert idx into i,j indices of an nxn matrix
    # into the flatten idx of its lower triangular matrix
    # BY KORN!!
    def _tril_idx_to_ij(self, idx, diag=False):
        i = floor((-1 + sqrt(1 + 8 * idx)) / 2) + (0 if diag else 1)
        j = idx - i * (i - 1) // 2

        return i, j

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self._tril_idx_to_ij(idx, diag=self.diag)
        elif isinstance(idx, tuple) and len(tuple) == 2:
            return self._tril_ij_to_idx(**idx, diag=self.diag)
        else:
            raise Exception("Wrong argument!")
