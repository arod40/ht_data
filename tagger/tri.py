from bisect import bisect_right


class tril:
    def __init__(self, n, diag=False):
        self.n = n
        self.diag = diag

    def __len__(self):
        return self.n

    def __getitem__(self, i):
        if self.diag:
            i += 1
        return i * (i + 1) // 2


class TriL:
    def __init__(self, n, diag=False):
        self.n = n
        self.diag = diag

    # O(1) solution to convert i,j into flatten indices of the lower triangular matrix
    def _tril_ij_to_idx(self, i, j, diag=False):
        if not diag:
            i -= 1
        if i < 0 or i > j:
            raise Exception("Wrong indices for lower triangular matrix!")
        return i * (i - 1) / 2 + j

    # O(log n) solution to convert idx into i,j indices of an nxn matrix
    # into the flatten idx of its lower triangular matrix
    def _tril_idx_to_ij(self, idx, n, diag=False):
        i = bisect_right(tril(n, diag=diag), idx)
        i0 = i + (1 if diag else 0)
        j = idx - i0 * (i0 - 1) // 2 

        return i, j

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self._tril_idx_to_ij(idx, self.n, diag=self.diag)
        elif isinstance(idx, tuple) and len(tuple) == 2:
            return self._tril_ij_to_idx(**idx, diag=self.diag)
        else:
            raise Exception("Wrong argument!")