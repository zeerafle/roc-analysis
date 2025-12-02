---
theme: seriph
background: https://cover.sli.dev
title: ROC Analizine Giriş
info: |
  ## An Introduction to ROC Analysis
  Based on the paper by Tom Fawcett (2006).
drawings:
  persist: false
transition: slide-left
mdc: true
layout: intro
---

# ROC Analizine Giriş

> Tom Fawcett'in makalesinden

Vauwez Sam El Fareez

20249258020@cumhuriyet.edu.tr

<div class="abs-br m-6 flex gap-2">
  <a href="https://github.com/zeerafle/roc-analysis" target="_blank" alt="GitHub"
    class="text-xl slidev-icon-btn opacity-50 !border-none !hover:text-white">
    <carbon-logo-github />
  </a>
</div>

---

# ROC Nedir

**Receiver Operating Characteristics (ROC)** eğrisi, sınıflandırıcıları düzenlemek ve performanslarını görselleştirmek için kullanıslıdır.

-   **Köken**: Sinyal algılama teorisi (II. Dünya Savaşı radar analizi).
-   **Benimsenme**: Tıbbi karar verme süreçlerinde ve daha sonra makine öğrenimi topluluğu tarafından benimsenmiştir.
-   **Neden?**: Doğruluk (Accuracy) genellikle yeterli değildir!
    -   Sınıf dağılımları çarpık olabilir (ör. %99 negatif, %1 pozitif).
    -   Hata maliyetleri eşit olmayabilir (Yanlış Pozitif vs Yanlış Negatif).

ROC analizi, bu ödünleşimleri anlamamıza yardımcı olur.

---

# Karmaşıklık Matrisi (Confusion Matrix)

İkili sınıflandırma problemi (Pozitif vs Negatif) için dört olası sonuç vardır:

| | Gerçek Pozitif | Gerçek Negatif |
|---|---|---|
| **Tahmin Edilen Pozitif** | **Doğru Pozitif (TP)** <br> (İsabet) | **Yanlış Pozitif (FP)** <br> (Iskalama) |
| **Tahmin Edilen Negatif** | **Yanlış Negatif (FN)** <br> (Yanlış Alarm) | **Doğru Negatif (TN)** <br> (Doğru Red) |

Bunlardan temel metrikleri türetiriz:

-   **Doğru Pozitif Oranı (TPR)** (Duyarlılık - Recall, Sensitivity): $TPR = \frac{TP}{TP + FN}$
    -   *Pozitiflerin ne kadarını yakaladık?*
-   **Yanlış Pozitif Oranı (FPR)** (1 - Özgüllük - Specificity): $FPR = \frac{FP}{FP + TN}$
    -   *Negatiflerin ne kadarına yanlışlıkla pozitif dedik?*

---

# İnteraktif Karmaşıklık Matrisi

<InteractiveConfusionMatrix />

---
layout: two-cols
---

# ROC Uzayı

X ekseninde **FPR** ve Y ekseninde **TPR** çizilir.

-   **Sol-Üst (0, 1)**: Mükemmel Sınıflandırma.
    -   %0 Yanlış Pozitif, %100 Doğru Pozitif.
-   **Köşegen Çizgisi (y = x)**: Rastgele Tahmin.
    -   Rastgele tahmin yapan bir sınıflandırıcı bu çizgi üzerine düşer.
-   **Sağ-Alt (1, 0)**: Olası en kötü durum.
    -   Her zaman yanlış.
-   **Köşegenin Altı**: Rastgeleden daha kötü (daha iyi yapmak için tahminleri tersine çevirin!).

::right::

<div class="flex justify-center items-center h-full">
  <RocSpace />
</div>

---

# ROC Eğrisi

Çoğu sınıflandırıcı (Yapay Sinir Ağları veya Naive Bayes gibi) sadece bir sınıf etiketi değil, bir **skor** veya **olasılık** üretir.

-   Skoru bir etikete (Pozitif/Negatif) dönüştürmek için bir **eşik değeri (threshold)** seçmemiz gerekir.
-   **Yüksek Eşik**: Muhafazakar. Az Yanlış Pozitif, ancak düşük Doğru Pozitif Oranı. (Sol-alt)
-   **Düşük Eşik**: Liberal. Yüksek Doğru Pozitif Oranı, ancak çok sayıda Yanlış Pozitif. (Sağ-üst)

Eşik değerini $-\infty$'dan $+\infty$'a değiştirerek **ROC Eğrisi**ni çizeriz.

---
layout: center
---

# İnteraktif ROC Görselleştirme

**Ayrımı (Separation)** (problemin ne kadar kolay olduğu) ve **Eşik Değerini (Threshold)** ayarlayın.

<InteractiveROC />

---
layout: center
---

# Deneysel ROC Eğrisi (Spam Örneği)

Gerçek dünya ROC eğrileri genellikle "tırtıklı"dır (basamak fonksiyonları), çünkü sonlu sayıda test örneğinden oluşturulurlar.

<SpamRoc />

<!-- Explain how to draw the roc curve -->

---

# Eğri Altındaki Alan (AUC)

**AUC** (ROC Eğrisi Altındaki Alan), eğriyi tek bir sayıya indirger.

-   **Aralık**: 0.5 (Rastgele) ile 1.0 (Mükemmel) arası.
-   **Yorum**: Sınıflandırıcının rastgele seçilen bir pozitif örneği, rastgele seçilen bir negatif örnekten daha yüksek sıralama olasılığı.
-   **Wilcoxon İstatistiği**: AUC, Wilcoxon-Mann-Whitney istatistiğine eşdeğerdir.

$$ AUC = P(Score(x^+) > Score(x^-)) $$

Bu, eşik değerinden bağımsız bir **sıralama kalitesi** ölçüsüdür.

---

# AUC Hesaplama: Yamuk Yöntemi

Sıralanmış tahmin listesinde aşağı doğru ilerlerken oluşan yamukların alanlarını toplayarak AUC'yi hesaplarız.

<InteractiveAucCalculation />

<!-- The reason points 5 and 6 create a diagonal line instead of a jagged step is because they have the exact same score (0.50).

In ROC analysis, when multiple instances have the same score (a "tie"), we cannot distinguish between them. The standard approach—and the one recommended in the paper—is to treat them as a single group.

Jagged Steps (Distinct Scores): Usually, we process one point at a time.

If it's Positive, we go Up (TP increases).
If it's Negative, we go Right (FP increases).
This creates the "staircase" look.
Diagonal Line (Tied Scores): When a Positive and a Negative have the same score, we can't say one is ranked higher than the other.

Instead of arbitrarily picking one first (which would create a step), we average their effect.
We move Up and Right simultaneously.
This creates a diagonal segment (a trapezoid).
This

is exactly why the Trapezoid Method is used for AUC calculation—it correctly handles these ties by calculating the area under that diagonal, rather than overestimating or underestimating with a rectangle. -->

---

# İnteraktif AUC Görselleştirme

Sınıflandırıcının çalışma noktasını (TP ve FP) değiştirmek için kaydırıcıları hareket ettirin.
**ROC Eğrisi**nin nasıl büküldüğünü ve **AUC**'nin nasıl değiştiğini görün.

<InteractiveAuc />

---

# Çok Sınıflı ROC: Biri-Hepsine-Karşı (One-vs-All)

$N > 2$ sınıfı ele almak için **Biri-Hepsine-Karşı** yaklaşımını kullanırız.
$N$ adet ayrı ROC grafiği oluştururuz. Her $C_i$ sınıfı için:

<InteractiveMultiClass />


<!-- -   **Pozitif**: $C_i$ Sınıfı
-   **Negatif**: Diğer tüm sınıflar ($\neg C_i$)

Why it should be straight lines: In this specific "One-vs-All" example, we are working with a fixed Confusion Matrix. This means we have a single fixed threshold, resulting in exactly one point (TPR, FPR) in ROC space. We don't have the data to draw the full curve. -->

---

# Çok Sınıflı AUC

## Ağırlıklı Ortalama Yöntemi

Bu yöntem, daha önce açıklanan "Biri-Hepsine-Karşı" grafiklerine bakarak toplam AUC'yi hesaplar.

$$AUC_{total} = \sum_{c_i \in C} AUC(c_i) \cdot p(c_i)$$

Hesaplama: Her bir ayrı sınıf grafiği için (Kedi vs. Hepsi, Köpek vs. Hepsi, vb.) AUC'yi hesaplayın. Ardından, her sınıfın veride ne kadar yaygın olduğuna ("yaygınlık" - prevalence) bağlı olarak bu skorların ağırlıklı ortalamasını hesaplarsınız.

$$AUC_{total} = (AUC_{Kedi} \times p_{Kedi}) + (AUC_{Köpek} \times p_{Köpek}) + (AUC_{\text{Kuş}} \times p_{\text{Kuş}})$$

<hr></hr>

**$p_{Kedi}$**: Veri setinizdeki Kedilerin **yaygınlığı** (olasılığı). Şu şekilde hesaplanır:

$$p_{Kedi} = \frac{\text{Toplam Kedi Sayısı}}{\text{Veri Setindeki Toplam Örnek Sayısı}}$$

*(Bu mantığı Köpek ve Kuş için tekrarlayın).*

<!-- By multiplying by $p$, classes that appear more often in your data contribute more to the final score[cite: 842]. If 90% of your data are Dogs, the model's ability to recognize Dogs effectively becomes 90% of the final grade. -->

---

# Çok Sınıflı AUC

## Çiftli (Pairwise) Yöntem

Bu yöntem, her sınıfta kaç öğe olduğunu göz ardı ederek sınıfların birbirinden ne kadar farklı olduğunu ölçmeye çalışır.

Hesaplama: Sınıfları gruplamak yerine, bu yöntem her olası sınıf çiftine bakar (ör. Kedi vs. Köpek, Kedi vs. Kuş, Köpek vs. Kuş).

- Her çift için AUC'yi hesaplar.
- Nihai bir skor (M olarak adlandırılır) elde etmek için bu çiftli AUC'lerin ortalamasını alır.

Artılar/Eksiler: Sınıftaki öğe sayısı değiştiği için değişmeyen bir skor istiyorsanız (sınıf dağılımına duyarsız) bu ölçüm mükemmeldir. Ancak, tamamen matematikseldir ve tek bir grafik yüzeyi olarak görselleştirilmesi zordur.

<!-- Take every pair of classes, compute the AUC for that binary problem, and average across pairs. That gives a multiclass AUC that doesn’t depend on class frequencies. -->

---
layout: two-cols
gap: 8
---

# Dışbükey Örtü (Convex Hull) & Eş-Performans

- __ROC Dışbükey Örtüsü (ROCCH)__
  - "En iyi" sistem, tüm sınıflandırıcıların dışbükey örtüsüdür.
  - **A** ve **C** sınıflandırıcıları örtüyü oluşturur.
  - **B** ve **D** sınıflandırıcıları optimal altıdır (örtünün altında).

- __Eş-Performans Doğruları (Iso-Performance Lines)__
  - Eşit **Beklenen Maliyet** doğruları.
  - Eğim $m = \frac{P(N) \cdot C(FP)}{P(P) \cdot C(FN)}$.
  - Optimal nokta, $m$ eğimine sahip doğruya teğet olan noktadır.

::right::

<div class="flex justify-center items-center h-full">
  <InteractiveConvexHull />
</div>

---

# Precision-Recall (Kesinlik-Duyarlılık) vs ROC

<InteractivePrVsRoc />

**Pratik Kural**: Farklı sınıf dengelerinde kararlı bir metrik istediğinizde ROC kullanın. "Samanlıkta iğne aramak" (nadir pozitif sınıf) sizin için önemliyse ve yanlış pozitifler çok pahalıysa PR kullanın.

<!-- Sometimes people use **Precision-Recall (PR)** curves instead.

-   **Precision**: $\frac{TP}{TP + FP}$ (How many predicted positives are actually positive?)
-   **Recall**: Same as TPR.

**Difference**:
-   **ROC** is insensitive to class skew. If negatives increase by 10x, FPR stays the same (TN increases proportionally).
-   **PR** is sensitive to class skew. If negatives increase, False Positives might increase, lowering Precision. -->

---

# Sonuç

-   **ROC Analizi**, özellikle dengesiz veriler veya eşit olmayan maliyetlerle sınıflandırıcı performansını değerlendirmek için sağlam bir yol sağlar.
-   **ROC Uzayı**, sınıflandırıcı performansını (eğri) çalışma koşullarından (eşik değeri) ayırır.
-   **AUC**, sıralama yeteneğinin tek sayılık bir özetini verir.
-   **Dışbükey Örtü (Convex Hull)**, en iyi sınıflandırıcı setini seçmeye yardımcı olur.

---
layout: end
---

# Dinlediğiniz İçin Teşekkür Ederim!
