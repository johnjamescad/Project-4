# Project-4  
  
## Quick Links  
[Project Plan](Documents/UofT-Project04-Plan.pdf)  
  
Google Colab:  
[ETL](https://colab.research.google.com/drive/1GpQ29JKaLhXdqncHfyx6sBMs4xKNJHgV?usp=sharing)  
[EDA Work](https://colab.research.google.com/drive/1XUSxIBGcxdADNkhOIuPoS6MyIlEaA7nr?usp=sharing)  
[ML Work](https://colab.research.google.com/drive/114IJn53fqlRZWbhUOkqoIbAn23Wv0SmR?usp=sharing)  
  
Tableau:  
[Tableau Public](https://public.tableau.com/views/Project4-HeartDisease/Story1?:language=en-US&publish=yes&:display_count=n&:origin=viz_share_link)  
  
Github Pages:  
[Heart disease prediction app](https://johnjamescad.github.io/Project-4/)  
  
## Table of Contents  
* Data Preprocessing  
  * [Exploratory Data Analysis or EDA](#user-content-exploratory-data-analysis-eda)  
* [Machine Learning](#user-content-machine-learning)  
  
### Exploratory Data Analysis \(EDA\)  
We started with Pandas describe\( \) method.  
![Pandas describe of the data](Screenshots/Data-Describe.png)  
  
After which we created Pearson Correlation Coefficient matrix and plotted it, which should reasonable correlation between the feature variables and the target.  
![Pandas describe of the data](Screenshots/Correlation.png)  
  
We continued our analysis by looking for outliers, plotting with box plots and scatter plots for all 13 features against the target.
![age vs target](Screenshots/EDA-01.png)  
![sex vs target](Screenshots/EDA-02.png)  
![cp vs target](Screenshots/EDA-03.png)  
![trestbps vs target](Screenshots/EDA-04.png)  
![chol vs target](Screenshots/EDA-05.png)  
![fbs vs target](Screenshots/EDA-06.png)  
![restecg vs target](Screenshots/EDA-07.png)  
![thalach vs target](Screenshots/EDA-08.png)  
![exang vs target](Screenshots/EDA-09.png)  
![oldpeak vs target](Screenshots/EDA-10.png)  
![slope vs target](Screenshots/EDA-11.png)  
![ca vs target](Screenshots/EDA-12.png)  
![thal vs target](Screenshots/EDA-13.png)  

### Machine Learning  
To measure the performance of the Machine Learning model, we use precision, recall and accuracy (f-score).  
  
The precision of a model describes how many detected items are truly relevant. It is calculated by dividing the true positives by overall positives.  
  
Recall is a measure of how many relevant elements were detected. Therefore it divides true positives by the number of relevant elements.  
  
The F-score is a measure of a test's accuracy. It is calculated from recall and precision values.  
  