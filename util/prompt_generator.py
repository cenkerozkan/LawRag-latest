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
        # Seçilen PDF'leri XML formatına uygun hale getir
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
                            <sample tag="borçlar_kanunu">
                                <question>
                                    Sözleşmede yazılı olmayan bir zarar için tazminat isteyebilir miyim?
                                </question>
                                <answer>
                                    TBK Madde 49: “Haksız fiil sonrasında doğan zararların tazmini, bu Kanun’un 50 nci maddesi hükümlerine göre yapılır.”  
                                    TBK Madde 50: “Sözleşmeden doğmayan zararlardan sorumluluk, kusur esasına dayanır. Kusurun ispatı zarara uğrayan, kusurun varlığı ise zararı doğuran kişiye aittir.”  
                                    TBK Madde 56: “Maddi tazminat, zararın gerçekleştiği andaki objektif değerlerle hesaplanır; manevi tazminat ise kişinin çektiği elem ve ıstıraba göre belirlenir.”
                                </answer>
                            </sample>
                        
                            <sample tag="iş_kanunu">
                                <question>
                                    İşveren beni haklı neden olmadan işten çıkarırsa ne yapabilirim?
                                </question>
                                <answer>
                                    4857 sayılı İş Kanunu Madde 18/II: “Geçerli sebep olmadan yapılan fesih bildirimleri geçersizdir.”  
                                    Madde 20: “Geçersiz sebeple yapılan fesih halinde işçi, işe iade davası açabilir; işe başlatılmadığı takdirde en az dört ila sekiz aylık ücreti tutarında tazminata hak kazanır.”  
                                    Madde 21: “İşveren, fesih bildirimini yazılı yapmak ve geçerli nedeni açıkça belirtmek zorundadır.”
                                </answer>
                            </sample>
                            <sample tag="sinai_mülkiyet_kanunu">
                                <question>
                                    Markam başkası tarafından izinsiz kullanılırsa ne yapabilirim?
                                </question>
                                <answer>
                                    6769 sayılı Sınai Mülkiyet Kanunu Madde 29/II: “Marka hakkına tecavüz teşkil eden fiiller için durdurma, el koyma ve tazminat davası açılabilir.”  
                                    Madde 34: “Haksız kullanım halinde maddi ve manevi tazminat, haksız fiilin son bulduğu andaki zarara göre hesaplanır.”  
                                    Madde 36: “Ürünlerin piyasadan toplattırılması veya imhası talep edilebilir.”
                                </answer>
                            </sample>
                        
                            <sample tag="türk_ceza_kanunu">
                                <question>
                                    Birine sosyal medyada hakaret edersem ne olur?
                                </question>
                                <answer>
                                    TCK Madde 125/I: “Bir kimsenin onur, şeref veya saygınlığına yönelik hakaret eylemleri bir yıldan üç yıla kadar hapis veya adli para cezasıyla cezalandırılır.”  
                                    Madde 125/II-3: “Aleniyet taşıyan yerlerde veya yöntemlerle işlenen hakaret, cezanın alt ve üst sınırlarında artırım sebebidir.”  
                                    Madde 125/III: “Hâkim, kişilerin sosyal konumu ve eylemin ağırlığına göre cezada indirim veya artırıma hükmeder.”
                                </answer>
                            </sample>
                        
                            <sample tag="türk_ticaret_kanunu">
                                <question>
                                    Şirket ortağının sorumluluğu nedir?
                                </question>
                                <answer>
                                    TTK Madde 576: “Anonim şirket ortakları, taahhüt ettikleri sermaye paylarını iktisap etmek zorundadır.”  
                                    Madde 580: “Limited şirket ortaklarının sorumluluğu, taahhüt ettikleri sermaye payları ile sınırlıdır; şirkete karşı mali sorumlulukları sermayeleriyle ölçülür.”  
                                    Madde 597: “Haksız defter tutma veya yanlış beyanlar için ortaklar ve yönetim kurulu üyeleri cezai ve hukuki sorumluluk altındadır.”
                                </answer>
                            </sample>
                        
                            <sample tag="anayasa">
                                <question>
                                    İfade özgürlüğüm kısıtlanabilir mi?
                                </question>
                                <answer>
                                    Anayasa Madde 26/I: “Herkes, düşünce ve kanaatlerini söz, yazı, resim veya başka yollarla açıklama ve yayma hakkına sahiptir.”  
                                    Madde 26/II: “Bu hak, milli güvenlik, kamu düzeni, suç işlenmesinin önlenmesi, genel ahlak, başkalarının hak ve itibarını koruma amacıyla kanunla sınırlanabilir.”  
                                    Madde 28: “Basın hürdür, sansür edilemez; ancak basın yoluyla işlenen suçlar kanunla düzenlenir.”
                                </answer>
                            </sample>
                        
                            <sample tag="kvkk">
                                <question>
                                    Şirketler kişisel verimi izinsiz işleyebilir mi?
                                </question>
                                <answer>
                                    6698 sayılı KVKK Madde 5/I: “Kişisel veriler, ilgili kişinin açık rızası olmaksızın işlenemez.”  
                                    Madde 6/II: “Kanunlarda öngörülmesi veya fiili imkânsızlık gibi istisnai haller dışında verilerin işlenebilmesi için açık rıza aranır.”  
                                    Madde 12: “Veri sorumlusu, işlem faaliyetlerini ilgili kişiye bildirerek şeffaflık prensibini sağlar.”
                                </answer>
                            </sample>
                        
                            <sample tag="medeni_kanun">
                                <question>
                                    Boşanma davasında mal paylaşımı nasıl yapılır?
                                </question>
                                <answer>
                                    TMK Madde 218: “Edinilmiş mallara katılma rejimi esas olup, boşanma halinde edinilmiş mallar yarı yarıya paylaşılır.”  
                                    Madde 219: “Kişisel mallar, miras veya bağış yoluyla edinilen mallar paylaşma dışındadır.”  
                                    Madde 220: “Hakim, eşlerin katkı ve ihtiyaç durumlarını gözeterek farklı bir paylaşım kararı verebilir.”
                                </answer>
                            </sample>
                        
                            <sample tag="ceza_muhakemeleri_kanunu">
                                <question>
                                    Savcılık ifadesine gitmeden avukat talep edebilir miyim?
                                </question>
                                <answer>
                                    CMK Madde 147/I: “Şüpheli veya sanık ifadesi alınmadan önce, müdafi talep etme hakkı kendisine bildirilir.”  
                                    Madde 147/II: “Müdafiin bulunmaması halinde, müdafi atanması sağlanır ve ifade bu kişi huzurunda alınır.”  
                                    Madde 148: “Avukatın görev ve yetkileri, soruşturmanın her aşamasında şüpheliyi korumaya yöneliktir.”
                                </answer>
                            </sample>
                        
                            <sample tag="infaz_kanunu">
                                <question>
                                    Denetimli serbestlik nedir?
                                </question>
                                <answer>
                                    5275 sayılı Kanun Madde 105/A: “Denetimli serbestlik, hükümlünün ceza infaz kurumundan çıkarak toplum içinde denetime tabi tutulmasıdır.”  
                                    Madde 107: “Denetimli serbestlik süresi, kalan cezanın üçte biriyle sınırlıdır.”  
                                    Madde 109: “Kuruma yeniden dönme kararı, yükümlülüklerin ihlali hâlinde verilir.”
                                </answer>
                            </sample>
                        
                            <sample tag="vergi_kanunu">
                                <question>
                                    Vergi borcumu ödememem durumunda ne olur?
                                </question>
                                <answer>
                                    VUK Madde 18: “Vergi aslı ve gecikme faizi birlikte tahsil edilir.”  
                                    Madde 51: “Ödeme emri tebliğinden itibaren verilen süre içinde ödenmeyen borç, cebri icraya intikal eder.”  
                                    Madde 55: “Haciz işlemi önce nakdi ve banka hesaplarına, sonra taşınır ve taşınmaz mal varlıklarına uygulanır.”
                                </answer>
                            </sample>
                        
                            <sample tag="rekabet_kanunu">
                                <question>
                                    Bir firmanın tekelleşmesi hukuka uygun mudur?
                                </question>
                                <answer>
                                    4054 sayılı Kanun Madde 6/I: “Piyasada hâkim durumun kötüye kullanılması yasaktır.”  
                                    Madde 7: “Rekabeti önemli ölçüde olumsuz etkileyecek birleşme ve devralmalar Rekabet Kurulu onayına tabidir.”  
                                    Madde 16: “Yaptırım kararlarına uymayanlara idari para cezası uygulanır.”
                                </answer>
                            </sample>
                        
                            <sample tag="tüketici_kanunu">
                                <question>
                                    Aldığım ürün arızalı çıkarsa ne yapmalıyım?
                                </question>
                                <answer>
                                    6502 sayılı Kanun Madde 11/I: “Ayıplı mal halinde tüketici; onarım, değişim, bedel iadesi veya ayıp oranında indirim talep edebilir.”  
                                    Madde 13: “Tüketici, talep ettiği hakkı satıcıya bildirdiğinde satıcı 20 iş günü içinde yerine getirmek zorundadır.”  
                                    Madde 14: “Bu süre içinde işlem yapılmazsa tüketici diğer haklarını talep edebilir.”
                                </answer>
                            </sample>
                        
                            <sample tag="e_ticaret_kanunu">
                                <question>
                                    İstenmeyen e-postalar yollanması suç mudur?
                                </question>
                                <answer>
                                    6563 sayılı Kanun Madde 6/I: “Ticari elektronik iletiler, alıcının önceden onayı alınmadan gönderilemez.”  
                                    Madde 6/II: “İleti Yönetim Sistemi’ne (İYS) kayıt zorunludur.”  
                                    Madde 17: “Kurallara uymayanlara BTK tarafından idari para cezası verilir.”
                                </answer>
                            </sample>
                        
                            <sample tag="vergi_usul_kanunu">
                                <question>
                                    Vergi kaçıran biri hakkında ne tür işlemler yapılır?
                                </question>
                                <answer>
                                    VUK Madde 359/I: “Vergi zıyaı ve kaçakçılığı fiilleri cezai müeyyidelere tabidir.”  
                                    Madde 359/II: “Hapis cezası veya adli para cezası verilir; ayrıca vergi ziyaı tutarı tahsil edilir.”  
                                    Madde 370: “Fiilin ağırlığına göre hapis süresi belirlenir.”
                                </answer>
                            </sample>
                        
                            <sample tag="gelir_vergisi_kanunu">
                                <question>
                                    Freelance çalışan biri gelir vergisi öder mi?
                                </question>
                                <answer>
                                    GVK Madde 65: “Serbest meslek kazançları gelir vergisine tabidir.”  
                                    Madde 67: “Serbest meslek erbabı, kazançlarını defter tutarak belgelendirmekle yükümlüdür.”  
                                    Madde 86: “Yıllık beyanname verme süresi, takip eden yılın Mart ayının son günü kadardır.”
                                </answer>
                            </sample>
                        
                            <sample tag="kabahatler_kanunu">
                                <question>
                                    Kamu alanında sigara içmek hangi cezayı gerektirir?
                                </question>
                                <answer>
                                    5326 sayılı Kanun Madde 39/I: “Tütün ürünlerinin kapalı veya kamuya açık kapalı alanlarda tüketilmesi yasaktır.”  
                                    Madde 39/III: “Bu hükme uymayanlara 100 TL idari para cezası uygulanır.”  
                                    Madde 2: “Cezanın tasarufu polis veya zabıta tarafından düzenlenen tutanakla yerine getirilir.”
                                </answer>
                            </sample>
                        
                            <sample tag="hukuk_muhakemeleri_kanunu">
                                <question>
                                    Dava açmadan önce arabuluculuk zorunlu mu?
                                </question>
                                <answer>
                                    HMK Madde 3: “Kanunda yazılı dava şartlarına uyulmadan dava açılamaz.”  
                                    6325 sayılı Arabuluculuk Kanunu Madde 4: “Belirli hukuk uyuşmazlıklarında arabuluculuk dava şartı olarak düzenlenmiştir.”  
                                    HMK Madde 4: “Arabuluculuk zorunluluğu iş, ticaret, tüketici ve bazı alacak davalarında geçerlidir.”
                                </answer>
                            </sample>
                        
                            <sample tag="idari_yargılama_usulü_kanunu">
                                <question>
                                    İdareye karşı dava açmak için süre ne kadardır?
                                </question>
                                <answer>
                                    2577 sayılı Kanun Madde 7: “İdarî işlemlere karşı iptal davası açma süresi 60 gündür.”  
                                    Madde 8: “Süre, ilgilinin yazılı bildirim veya ilanen öğrenme tarihinden itibaren başlar.”  
                                    Madde 9: “Hak düşürücü bu süreler kesin olup uzatılamaz.”
                                </answer>
                            </sample>
                        
                            <sample tag="icra_ve_iflas_kanunu">
                                <question>
                                    Borçluya ödeme emri gönderildikten sonra ne olur?
                                </question>
                                <answer>
                                    İİK Madde 58/I: “Ödeme emrine tebliğ tarihinden itibaren borçluya itiraz hakkı verilir.”  
                                    Madde 58/II: “Yedi gün içinde itiraz edilmezse takip kesinleşir ve haciz yoluna gidilir.”  
                                    Madde 68: “İtiraz hâlinde, icra mahkemesinde itirazın iptali davası açılabilir.”
                                </answer>
                            </sample>
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


prompt_generator = PromptGenerator()