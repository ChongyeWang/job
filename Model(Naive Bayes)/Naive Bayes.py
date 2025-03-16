# First, we are importing the necessary libraries
import pandas as pd # pandas is used to reading and understanding the tabuler format of data  
import numpy as np # numpy is used for advanced calculations
import seaborn as sns # Seaborn to display some specific kind of graphs
import matplotlib.pyplot as plt # for ploting the graphs
from sklearn.feature_extraction.text import TfidfVectorizer  # we are importing the vectorizer modul, to convert the digital text into numerical  
from sklearn.model_selection import train_test_split # we need to split the data into trainging and testing 
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from wordcloud import WordCloud  # to display the word cloud 

# Loadong the dataset
file_path = 'Updated_Resume_with_Class.csv'
resume_df = pd.read_csv(file_path)

# Initially cleaning the first few rows of the dataset 
resume_df['Resume_str'] = resume_df['Resume_str'].fillna("")
# Check if the dataset is loaded correctly
print(resume_df.info())  # Overview of dataset
print(resume_df.head())  # Preview the first few rows

# Confirm no missing values in 'Resume_str'
print("NaN values in 'Resume_str':", resume_df['Resume_str'].isnull().sum())

#Now, Data Cleaning

# We are droping columns with more than 95% NaN values
threshold = 0.95
resume_df = resume_df.loc[:, resume_df.isnull().mean() < threshold]

# And columns with a single unique value
resume_df = resume_df.loc[:, resume_df.nunique() > 1]

# Ensure the 'Class' column is correctly encoded (Flagged = 1, Unflagged = 0)
resume_df['Class'] = resume_df['Class'].map({'Unflagged': 0, 'Flagged': 1})

# Filter rows with exactly 5 non-NaN (valid) values, including 'Class'
valid_row_mask = resume_df.notna().sum(axis=1) == 5

# Apply the mask to filter rows
resume_df = resume_df[valid_row_mask]

# Fill missing values in the 'Category' column (if needed)
resume_df['Category'].fillna('Unknown', inplace=True)

# Drop any remaining rows where 'Class' is NaN
resume_df = resume_df.dropna(subset=['Class'])

# Convert 'Class' column to integers (in case NaNs were removed)
resume_df['Class'] = resume_df['Class'].astype(int)

# Verifying the cleaned dataset
print(f"Shape after cleaning: {resume_df.shape}")
print("Remaining NaN values:", resume_df.isnull().sum().sum())
print("Unique values in 'Class':", resume_df['Class'].unique())
print(resume_df.head())

print("Unique values in 'Class':", resume_df['Class'].unique())
print("Unique values in 'Category':", resume_df['Category'].unique())
print("Number of rows:", resume_df.shape[0])

# Plotting the distribution of Flagged and Unflagged classes
plt.figure(figsize=(8, 6))
sns.countplot(x='Class', data=resume_df, palette='viridis')
plt.title('Count of Flagged and Unflagged Resumes', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Class', fontsize=14)
plt.ylabel('Count', fontsize=14)
plt.xticks(ticks=[0, 1], labels=['Unflagged', 'Flagged'], fontsize=12)
plt.yticks(fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# Plotting the distribution of Categories as a Bar Chart
plt.figure(figsize=(12, 8))
category_counts = resume_df['Category'].value_counts()

sns.barplot(
    x=category_counts.index,
    y=category_counts.values,
    palette='viridis'
)

# Add labels and title
plt.title('Distribution of Categories', fontsize=20, fontweight='bold', pad=20)
plt.xlabel('Category', fontsize=16)
plt.ylabel('Count', fontsize=16)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.yticks(fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Add annotations to the bars
for index, value in enumerate(category_counts.values):
    plt.text(index, value + 5, f'{value}', ha='center', fontsize=10)

plt.tight_layout()
plt.show()

# Plotting the distribution of Categories as a Pie Chart
plt.figure(figsize=(12, 12))
category_counts = resume_df['Category'].value_counts()

# Create pie chart
plt.pie(
    category_counts.values,
    labels=category_counts.index,
    autopct='%1.1f%%',
    startangle=140,
    colors=sns.color_palette('viridis', n_colors=len(category_counts)),
    wedgeprops={'edgecolor': 'black'}
)

# Add title
plt.title('Category Distribution', fontsize=20, fontweight='bold', pad=20)
plt.tight_layout()
plt.show()

# WordCloud for a specific category
category_name = 'HR'  # Example category
wc = WordCloud(max_words=2000, stopwords=WordCloud().stopwords).generate(
    str(resume_df[resume_df['Category'] == category_name]['Resume_str'])
)
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.title(f"WordCloud for Category: {category_name}")
plt.show()

# Apply TF-IDF vectorization
vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
X = vectorizer.fit_transform(resume_df['Resume_str'])
y = resume_df['Class']

# Display the feature names generated by the TF-IDF Vectorizer
feature_names = vectorizer.get_feature_names_out()
print("Sample features from TF-IDF Vectorizer:", feature_names[:20])  # Display the first 20 features

# Check for missing values in y
print("Number of NaN values in y:", y.isnull().sum())

# Drop rows with missing target values
resume_df = resume_df[~resume_df['Class'].isnull()]

# Recreate X and y
X = vectorizer.fit_transform(resume_df['Resume_str'])
y = resume_df['Class']

# Perform train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

print("Train-Test split completed successfully.")

from imblearn.over_sampling import SMOTE

# Apply SMOTE
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)

# Split the resampled data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

print("Class distribution after SMOTE:")
print(pd.Series(y_resampled).value_counts())

from imblearn.under_sampling import RandomUnderSampler

# Apply undersampling
undersampler = RandomUnderSampler(random_state=42)
X_balanced, y_balanced = undersampler.fit_resample(X_resampled, y_resampled)

# Check the class distribution after undersampling
print("Class distribution after undersampling:")
print(pd.Series(y_balanced).value_counts())


# Here we are spliting the undersampled data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_balanced, y_balanced, test_size=0.2, random_state=42)

from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# We are training the Naive Bayes model on the balanced dataset
Bayes_clf = MultinomialNB(alpha=3)
Bayes_clf.fit(X_train, y_train)

# Evaluate the model on the test set
y_pred_test = Bayes_clf.predict(X_test)

# Generates and prints the classification report
print("Classification Report (Naive Bayes):")
print(classification_report(y_test, y_pred_test))

# Generating and ploting the confusion matrix
cm = confusion_matrix(y_test, y_pred_test)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
plt.title("Confusion Matrix - Test Data (Naive Bayes)")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()
