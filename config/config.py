"""
This file contains necessary variables and constants for the application.
"""

CHUNK_SIZE = 1100
MESSAGE_HISTORY_SIZE = 300
GOOGLE_SEARCH_RESULT = 10
DOC_REPO_RESULT_K=10
# This is for making document retrieval much more easy.
# Change the lookup table to use the repository instances
LOOKUP_TABLE: dict = {
    "is_isci_kanun": lambda self, query, conversation_history: self._is_isci_kanun_repository.aretrieve(query, conversation_history),
    "borclar_kanun": lambda self, query, conversation_history: self._borclar_kanun_repository.aretrieve(query, conversation_history),
    "sinai_mulkiyet_kanun": lambda self, query, conversation_history: self._sinai_mulkiyet_kanun_repository.aretrieve(query, conversation_history),
    "turk_ceza_kanun": lambda self, query, conversation_history: self._turk_ceza_kanun_repository.aretrieve(query, conversation_history),
    "ceza_muhakeme_kanun": lambda self, query, conversation_history: self._ceza_muhakeme_kanun_repository.aretrieve(query, conversation_history),
    "elektronik_ticaretin_duzenlenmesi_hakkinda_kanun": lambda self, query, conversation_history: self._elektronik_ticaretin_duzenlenmesi_kanun_repository.aretrieve(query, conversation_history),
    "gelir_vergisi_kanunu": lambda self, query, conversation_history: self._gelir_vergisi_kanun_repository.aretrieve(query, conversation_history),
    "infaz_kanun": lambda self, query, conversation_history: self._infaz_kanun_repository.aretrieve(query, conversation_history),
    "kvkk_kanun": lambda self, query, conversation_history: self._kvkk_kanun_repository.aretrieve(query, conversation_history),
    "medeni_kanun": lambda self, query, conversation_history: self._medeni_kanun_repository.aretrieve(query, conversation_history),
    "rekabet_kanun": lambda self, query, conversation_history: self._rekabetin_korunmasi_kanun_repository.aretrieve(query, conversation_history),
    "tuketici_kanun": lambda self, query, conversation_history: self._tuketicinin_korunmasi_kanun_repository.aretrieve(query, conversation_history),
    "turk_ticaret_kanun": lambda self, query, conversation_history: self._turk_ticaret_kanun_repository.aretrieve(query, conversation_history),
    "vergi_usul_kanun": lambda self, query, conversation_history: self._vergi_usul_kanun_repository.aretrieve(query, conversation_history),
}