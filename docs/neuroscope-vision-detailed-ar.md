# NeuroScope — الفكرة الكاملة المفصّلة

## نظرة عامة

NeuroScope هو أداة بصرية لبناء نماذج التعلم العميق بدون كود. المستخدم يبني النموذج بصرياً عن طريق اختيار الموديل والإضافات (Hyperparameters) ويطلع بـ Notebook جاهز يشتغل عليه في Colab أو محلياً.

**التطبيق لا يشغّل أي كود ولا يحمّل أي dataset.** هو فقط يعرض الكود في Notebook ويصدّره للمستخدم.

---

## 1. واجهة العمل (Workspace)

### البداية
- واجهة فاضية (مثل n8n) بعلامة **plus (+)** في النص
- المستخدم يضغط على الـ plus ← يفتح قائمة/بانل بالمدلات المتاحة
- **أو** يسحب الموديل من البانل الأيمن ويحطه في واجهة العمل

### البانل الأيمن (Right Panel)
- يعرض قائمة المدفات فقط
- **يختفي** لما المستخدم يختار موديل
- لو المستخدم يحتاج يغيّر الموديل → يضغط على الـ Core Engine Block ← يشوف الخيارات

### بعد اختيار الموديل
- الموديل يظهر كـ **شكل كامل**: الـ Core Engine + Extensions Blocks + Cables
- الـ Core Engine **يشتغل فوراً** (Power On)

---

## 2. اختيار الموديل (Model Selector)

### الخطوات
1. **اختيار الموديل**: CNN (حالياً فقط — مستقبلاً YOLO, ResNet, EfficientNet)
2. **اختيار الإصدار** (لو موجود): مثل YOLOv11, v8, v10
3. **اختيار الحجم** (لو موجود): مثل YOLOv11n, s, m, l, x

### ملاحظات مهمة
- لو الموديل **مالوش إصدارات/أحجام** ← المستخدم يختار الموديل مباشرة ← البانل يتقفل ← الموديل يتفعّل
- كل موديل له **إضافات مختلفة** (extensions) لأن كل موديل له hyperparameters مختلفة
- مثال: YOLO عنده NMS (on/off, IOU threshold) لكن CNN مالوش

### تأثير الحجم على الشكل ثلاثي الأبعاد
- كل حجم أكبر = **طبقات 3D إضافية** على شكل الـ Core Engine
- مش بس تغيير حجم الـ Block، لكن إضافة تفاصيل ثلاثية الأبعاد أكثر

---

## 3. الـ Core Engine

### لما المستخدم يضغط عليه يشوف خيارات:
1. **Add Model** (مستقبلي — لعمل multi-modal)
2. **Remove/Change** (مستفي — لما نضيف مدفات أكتر)
3. **Custom** ← يفتح **Develop Mode**

### Develop Mode
- المستخدم يشوف **طبقات الموديل** والكود كامل
- خيارات: Freeze / Unfreeze / Remove / Add layers
- **طبقة الـ Head** هي الأهم:
  - تظهر في Develop Mode كافتراضي
  - **وتظهر كمان في الـ Main UI** من أول ما المستخدم يحمّل الموديل
  - كل موديل يحمّل بـ Head مختلف حسب عدد الـ classes في الـ Dataset
  - لازم يكون واضح: الـ Head الافتراضي + الـ Activation Function اللي يستخدمها

---

## 4. الـ Info Panel

### المحتوى
- لما المستخدم يختار الموديل ← الـ Core Engine يعرض **كل تفاصيل الموديل** في Info Panel
- لما المستخدم يضيف أي Extension (مثل Optimizer) ← المعلومات تضاف للـ Info Panel
- المعلومات تكون **نقاط مختصرة** (Brief/Primary info in points)

### الـ Head Layer
- يظهر تفاصيله في الـ Info Panel من أول تحميل الموديل
- الافتراضي + Activation Function

---

## 5. الـ Extensions (الإضافات / Hyperparameters)

### كيف تشتغل
1. المستخدم يضغط على Extension Block
2. البانل الأيمن يفتح بخيارات الـ Extension دي
3. المستخدم يختار_option
4. يضغط Apply
5. الكود يتنجّز في الـ Notebook
6. المعلومات تضاف للـ Info Panel

### كل موديل له Extensions مختلفة
- مش كل المدفات عندها نفس الـ Extensions
- Extensions تتحمل مع الموديل لما المستخدم يختاره
- مثال extensions لـ YOLO: Optimizer, Activation, Loss, Augmentation, NMS, Resolution
- مثال extensions لـ CNN: Optimizer, Activation, Loss (بدون NMS مثلاً)

---

## 6. الـ Notebook Window

### المميزات
- نافذة **قابلة للطي** (Collapsible) في أعلى يمين الواجهة
- **تفتح تلقائياً** لما المستخدم يختار الموديل
- **تفتح تلقائياً** لما المستخدم يغيّر أي Extension (الكود يتغير مباشرة)
- تقفل لما المستخدم يرجع للقائمة
- المستخدم يقدر يفتحها يدوياً لما يحتاج يشوف الكود
- يقدر **يشوف ويعديل** الكود

---

## 7. التصدير (Export)

### صيغ التصدير
1. **Notebook** (.ipynb) — جاهز لـ Colab
2. **Model YAML** — تعريف الموديل
3. أي صيغة مفيدة للمستخدم

### بعد التصدير
- المستخدم ياخد الـ Notebook على Colab
- يضيف سطور import الـ Dataset
- لو يشتغل محلياً ← يضيف سطور الـ environment و requirements

---

## 8. الـ Educational Layer

### كل Spec/Option عنده Info Panel يشرح:
- **إيه هو** — ببساطة، بدون مصطلحات معقدة
- **امتى تستخدمه** — إرشادات عملية
- **إيه اللي هيحصل لو اخترت غلط** — عواقب حقيقية

---

## 9. المستقبل (Future Features)
- إضافة مدفات أكتر (YOLO, ResNet, EfficientNet)
- Add Model (Multi-modal)
- Remove/Change Model
- Drag & Drop كامل
- تشغيل الكود مباشرة في المتصفح (GPU Backend)
- مقارنة موديلات جنب بعض

---

## الملاحظات التقنية
- الـ 3D shapes: Core Engine + Extensions + Cables
- كل Extension ليه لون حسب الفئة (Green=Training, Purple=Data, Yellow=Functional, Blue=Core)
- الـ Cables تتوهج لما Extension يتفعّل
- الـ Core Engine يشتغل من أول اختيار موديل

---

*آخر تحديث: 29 يونيو 2026*
