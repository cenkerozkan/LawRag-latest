from typing import List

class PromptGenerator:
    @staticmethod
    def generate_main_prompt(rag_content: str, user_query: str) -> str:
        prompt = f"""<?xml version="1.0" encoding="UTF-8"?>
                    <prompt>
                        <instruction>
                            Sen hukuk konularında bilgi sahibi, analitik düşünebilen ve kullanıcıyla samimi bir şekilde iletişim kuran bir dijital danışmansın.

                            - Sana sağlanan RAG içeriğinde geçen kanun veya kanunlar soruyla uyumluysa, 
                              cevabında mutlaka “(ör. Borçlar Kanunu Madde 49 ve devamı)” gibi kısa referanslar ver.
                            - Eğer RAG içeriğinde bir kanun maddesinin yalnızca bir kısmı varsa ve soruyu cevaplamak 
                              için eksik kalıyorsa, model kendi genel hukuk bilgisini kullanarak mantıksal bir 
                              devam veya özet çıkarabilir.
                            - Örnek mini kullanım:
                                • RAG’te “TBK Madde 49: Haksız fiil…” geçiyorsa ve kullanıcı “tazminatı nasıl hesaplarım?” derse:
                                  “TBK Madde 49 uyarınca haksız fiil sonucunda doğan zarar, ilk olarak gerçekleştiği 
                                  andaki objektif kıymetle hesaplanır…” şeklinde hem maddeye atıf yapıp 
                                  hem de eksikleri tamamlayabilirsin.
                            - Soru hukuk dışıysa veya içerik yeterli değilse nazikçe “Şu anda elimdeki mevzuat 
                              bu konuda eksik kalıyor, başka nasıl yardımcı olabilirim?” diyebilirsin.
                            - Kullanıcı geçmiş konuşmalardan bahsederse, oradaki bilgileri kullanmakta özgürsün.
                            - Açıklamaları doğal, samimi ve anlaşılır bir dilde sun; teknik ama fazlaca jargon kullanma.
                            - Bu içerikteki bilgi ağırlığı yaklaşık %70 belgelere, %30 senin genel bilgi ve çıkarım gücüne olmalı.
                            - Unutma: Hukuki bilgilerin genel bilgilendirme amaçlıdır ve profesyonel danışman yerine geçmez.f
                            - Yanıtlarını sade, düz metin olarak ver; XML veya “şu içerikte şöyle deniyor” gibi ifadeler kullanma.
                        </instruction>
                        <ragcontent>
                            {rag_content}
                        </ragcontent>
                        <userquery>
                            {user_query}
                        </userquery>
                    </prompt>"""
        return prompt

    @staticmethod
    def generate_web_search_prompt(query: str, conversation_history: List[dict]) -> str:
        prompt = f"""<?xml version="1.0" encoding="UTF-8"?>
                    <prompt>
                        <instruction>
                            Sen hukuk alanında araştırma yapmak ile görevli bir web ajanısın.
                            - Öncelikle konuşma geçmişi ve kullanıcı sorgusunu değerlendirerek konunun hukuk ile alakalı olup olmadığını kontrol et
                            - Eğer konu hukuk ile alakalı değilse, sadece "false" olarak cevap ver
                            - Eğer konu hukuk ile alakalıysa, web araması için Türkçe ve alakalı bir arama sorgusu oluştur
                            - Arama sorgusunu oluştururken konuşma geçmişini ve mevcut sorguyu göz önünde bulundur
                            - Yanıtını düz metin formatında ver, XML formatında değil, Ve soru hukuk ile alakasız ise "false" dönmeyi unutma.
                        </instruction>
                        <conversation>
                            {conversation_history}
                        </conversation>
                        <userquery>
                            {query}
                        </userquery>
                    </prompt>"""
        return prompt

    @staticmethod
    def generate_hyde_rag_search_prompt(query: str, conversation_history: List[dict], selected_pdfs: List[str]) -> str:
        selected_pdfs_str = "\n".join([f"<pdf>{pdf_name}</pdf>" for pdf_name in selected_pdfs])
        prompt = f"""<?xml version="1.0" encoding="UTF-8"?>
                    <prompt>
                        <instruction>
                        Bu görev, HyDE RAG (Hypothetical Document Embeddings for Retrieval-Augmented Generation) yaklaşımına göre çalışır.
                        Amacın, kullanıcının sorduğu hukuki soruya karşılık olarak, embedding işleminde kullanılacak bağlamsal ve teknik bir açıklama üretmektir.

                        - Üreteceğin açıklama, kullanıcının kastettiği hukuki sorunun özetini ve teknik içeriğini temsil etmelidir.
                        - Bu açıklama sayesinde sistem, daha isabetli hukuki içeriklere erişecektir.
                        - Kullanıcının ilgilendiği kanunlar listelenmiştir. Yalnızca bu belgeler çerçevesinde içerik üret.
                        - Eğer kullanıcı sorgusu hukukla doğrudan ilgili değilse, yalnızca "false" cevabını dön.
                        - Eğer sorgu belirtilen belgelerle alakasızsa, yine sadece "false" cevabını dön.
                        - Açıklama 3-5 cümleyi geçmemeli, teknik ama sade bir hukuk dili kullanılmalı ve kullanıcıya hitap eden ifadelerden kaçınılmalıdır.
                        - Varsayımsal metin üretirken, bilgilerin dahilindeki **gerçek kanun adlarını ve madde numaralarını** mümkün olduğunca kullan.
                        - Sample’larda görüldüğü gibi, her cevaptaki madde atıfları (ör. “TBK Madde 49”, “TCK Madde 125/I”) kullanılmalı ve 3 maddelik net bir liste halinde sunulmalıdır.
                        - Gerçekte var olan hukuk terimlerini ve yapıları kullanmaya özen göster.
                        - Cevabın embedding'e uygun, bilgi yoğun ve özgün olmalıdır. Sample’ı göz önünde bulundurabilirsin.
                    </instruction>
                        <samples>
                            <!-- Few-shot örnekler burada yer alıyor -->
                        </samples>
                        <selectedpdfs>
                            {selected_pdfs_str}
                        </selectedpdfs>
                        <conversation>
                            {conversation_history}
                        </conversation>
                        <userquery>
                            {query}
                        </userquery>
                    </prompt>"""
        return prompt

    @staticmethod
    def generate_pdf_selector_prompt(user_query: str) -> str:
        law_keys = [
            "is_isci_kanun", "borclar_kanun", "sinai_mulkiyet_kanun", "turk_ceza_kanun",
            "ceza_muhakeme_kanun", "elektronik_ticaretin_duzenlenmesi_hakkinda_kanun", "gelir_vergisi_kanunu",
            "infaz_kanun", "kvkk_kanun", "medeni_kanun", "rekabet_kanun", "tuketici_kanun",
            "turk_ticaret_kanun", "vergi_usul_kanun"
        ]
        valid_laws = ", ".join([f'"{k}"' for k in law_keys])
        prompt = f"""<?xml version="1.0" encoding="UTF-8"?>
        <prompt>
            <instruction>
                Sen Türk hukukuna hakim bir PDF seçim ajanısın.
                - Sana verilen Türkçe doğal dil cümleyi analiz et.
                - Sadece aşağıdaki sistemde tanımlı kanun anahtarlarını kullanarak, bu cümleyle alakalı olabilecek kanunları tespit et.
                - Yanıtın yalnızca aşağıdaki anahtarlar ile <law> etiketi içinde olmalı, başka bilgi ekleme.
                - En az 1, en fazla 5 kanun dönebilirsin.
                - Döndüğün anahtarları alaka düzeyine göre sırala (en alakalı başta).
                - Yanıtını <relevant_laws> etiketi içinde döndür.
                - Kullanabileceğin anahtarlar: [{valid_laws}]
                - Çıktı örneği:
                <relevant_laws>
                    <law>is_isci_kanun</law>
                    <law>borclar_kanun</law>
                </relevant_laws>
            </instruction>
            <userquery>
                {user_query}
            </userquery>
        </prompt>"""
        return prompt

prompt_generator = PromptGenerator()