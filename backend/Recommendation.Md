### **1. **Weight Calculation** (`calculate_weight`)**
The **weight** is a combination of the lawyer's normalized rating and experience, with the rating given 60% weight and experience 40%.

\[
\text{Normalized Rating} = \frac{\text{Rating}}{5}
\]
\[
\text{Normalized Experience} = \frac{\text{Experience}}{35}
\]
\[
\text{Weight} = 0.6 \times \text{Normalized Rating} + 0.4 \times \text{Normalized Experience}
\]

---

### **2. Recommendation Score Calculation** (`get_recommendation_score`)**

The **recommendation score** for a lawyer combines:
1. **Base Weight**: The normalized weight calculated from rating and experience.
2. **Time Factor**: Adjusts the score based on how recently the lawyer was recommended.
3. **Frequency Penalty**: Penalizes lawyers who are recommended more frequently.

#### **Base Weight:**
\[
\text{Base Weight} = \text{Weight} \times 1.5 \quad \text{if the lawyer has never been recommended before.}
\]

#### **Time Factor:**
\[
\text{Days Since Recommendation} = \text{Current Date} - \text{Last Recommended Date}
\]
\[
\text{Time Factor} = \min\left(\frac{\text{Days Since Recommendation}}{30}, 1.5\right)
\]

#### **Frequency Penalty:**
\[
\text{Frequency Penalty} = \frac{1}{1 + (\text{Recommendation Count} \times 0.1)}
\]

#### **Final Recommendation Score:**
\[
\text{Recommendation Score} = \text{Base Weight} \times \text{Time Factor} \times \text{Frequency Penalty}
\]

---

### **3. Lawyer Selection and Ranking** (`recommend_lawyer`)**
1. For each lawyer, calculate the **recommendation score** using the above formula.
2. Rank the lawyers in descending order of their scores.
3. Select the top 2 lawyers:
\[
\text{Top Lawyers} = \text{Sorted Lawyers}[0:2]
\]

---

### **4. Database Updates** (`update_recommendation_history`)**
When a lawyer is recommended, the following updates occur:
- Increment the **recommendation count**.
- Update the **last recommended date** to the current date.

---

### **Overall Logic:**
Given a specialization (sentiment), the system:
1. Retrieves all lawyers in the database matching the specialization.
2. Calculates the **recommendation score** for each lawyer.
3. Ranks the lawyers by their scores.
4. Returns the top two lawyers and updates their recommendation history.

---

This approach ensures that highly rated and experienced lawyers are prioritized while balancing recommendation frequency and recency.