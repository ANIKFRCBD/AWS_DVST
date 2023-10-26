import pandas as pd
from io import BytesIO
import base64
from django.shortcuts import render, redirect
import io
import sqlite3
import plotly.express as px
from plotly.offline import plot



# from .forms import CSVFileForm
# from .models import CSVFile

# Create your views here.
def index(request):
    return render(request, 'index.html')   

def header(request):
     return render(request, 'header.html')


#Uploading files and displaying
def upload_csv(request):
    context = {
        "df": None,
        "show_table": False,
        "rows_column_info": "",
        "dup_message": "",
        "null_message": "",
        "updated_rows_column_info": "",
    }

    if request.method == 'POST':
        #remove duplicate
        # Check if a file is included in the request
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']

            # Read the file content into a variable
            file_content = uploaded_file.read().decode('utf-8')

            # Create a Pandas DataFrame from the file content
            df = pd.read_csv(io.StringIO(file_content), index_col=[0])
            context['df'] = df.head(50)

            #printing number of rows and columns
            rows, columns = df.shape
            print(f"data shape = {rows}, {columns}")
            context['rows_column_info'] = f"Current data has {rows} rows and {columns} columns"

            #Data cleaning------------------------------
            #handling duplicate data
            if df.duplicated().sum() == 0:
                dup_message = f"No duplicates found in the data"
            else:
                dup_message = f"Total {df.duplicated().sum()}  duplicate rows were existed. These were removed"
            
            context['dup_message'] = dup_message

            #handling null values
            sum_of_null_data = 0
            for i in df.isna().sum():
                sum_of_null_data = i + sum_of_null_data

            if sum_of_null_data == 0:
                context['null_message'] = f"No rows with empty data found"
            else:
                df = df.dropna()

                context['df'] = df.head(50)
                context['null_message'] = f"{sum_of_null_data} rows with empty data found and removed"

            #printing updated number of rows and columns
            rows, columns = df.shape
            print(f"data shape = {rows}, {columns}")
            context['update_rows_column_info'] = f"Afer cleaning, the  dataset has {rows} rows and {columns} columns"

            context['show_table'] = True


    return render(request, 'upload_csv.html', context)


#data filter

#for giving commas between data
def concatenate_with_seperator(series, sep=', '):
     return sep.join(set(map(str, series)))

df = pd.read_csv('refined.csv')
df_only_show = df.copy()
df_only_show = df_only_show.head(500)



#==============database testing =========================
def database_test():
     try:
          tt = pd.read_csv('refined.csv')
          print("reading direct csv")
          tt.head(5)

          cnn = sqlite3.connect('db.sqlite3')
          print('connection successful')

          tt.to_sql('myProject', cnn, if_exists='replace')
          sql = 'Select * From myProject;'
          df_read = pd.read_sql(sql, cnn)
          print(df_read.head(10))
     except Exception as e:
          print(e)
     finally:
          if cnn:
               cnn.close()
     print('done')
          

#Data filter
def filter_data(request):
     context = {
          'df': df_only_show,
          'listed_df': False,
          'filter_title': '',
          'names': set(df['User Name']),
          'firms': set(df['Firm Name']),
         'years': set(df['Year']),
         'months': set(df['Month']),
         'records_found': '',
     }
     
     #session creation
     if 'unfiltered' in request.POST:
          request.session['selected_option'] = 'unfiltered'
     elif 'listed' in request.POST:
          request.session['selected_option'] = 'listed'
     elif 'not-listed' in request.POST:
          request.session['selected_option'] = 'not-listed'

     selected_option = request.session.get('selected_option', None)

     td = df
     ndf = df
     if request.method == 'POST':
          if selected_option:
               if selected_option == 'unfiltered':
                    context['df'] = df
               if selected_option == 'listed':
                    listed_df = td[td['Listed'] == 'Y']
                    context['df'] = listed_df
                    print('worked')
               if selected_option == 'not-listed':
                    notListed_df = td[td['Listed'] == 'N']
                    context['df'] = notListed_df  

          if 'industry_filter' in request.POST:
               industry_wise = df.groupby('Business Industry')[["Company Name", "Firm Name"]].agg(concatenate_with_seperator)
               company_name = industry_wise['Company Name'].apply(lambda x: ', '.join(set(x.split(', '))))
               firm_name = industry_wise['Firm Name'].apply(lambda x: ', '.join(set(x.split(', '))))

               industry_wise['Company Name'] = company_name
               industry_wise['Firm Name'] = firm_name
               context['df'] = industry_wise
               context['filter_title'] = 'Filtered by Industry Wise'

          if 'sector_filter' in request.POST:
               sector_wise = df.groupby('business Sector')[["Company Name", "Firm Name"]].agg(concatenate_with_seperator)
               company_name = sector_wise['Company Name'].apply(lambda x: ', '.join(set(x.split(', '))))
               firm_name = sector_wise['Firm Name'].apply(lambda x: ', '.join(set(x.split(', '))))

               sector_wise['Company Name'] = company_name
               sector_wise['Firm Name'] = firm_name
               context['df'] = sector_wise
               context['filter_title'] = 'Filtered by Sector Wise'

          if 'legal_status_filter' in request.POST:
               legal_wise = df.groupby('Legal status')[["Company Name", "Firm Name"]].agg(concatenate_with_seperator)
               company_name = legal_wise['Company Name'].apply(lambda x: ', '.join(set(x.split(', '))))
               firm_name = legal_wise['Firm Name'].apply(lambda x: ', '.join(set(x.split(', '))))

               legal_wise['Company Name'] = company_name
               legal_wise['Firm Name'] = firm_name
               context['df'] = legal_wise
               context['filter_title'] = 'Filtered by Legal Wise'

          #filtering name, firm etc.
          if 'selected_name' in request.POST:
               name = request.POST['selected_name']
               firm = request.POST['selected_firm']
               year = request.POST['selected_year']
               month = request.POST['selected_month']

               if selected_option == 'unfiltered':
                    ndf = context['df']
                    print('filter on whole data')
               elif selected_option == 'listed':
                    ndf = context['df']
                    print('filtering on listed')
               elif selected_option == 'not-listed':
                    ndf = context['df']
                    print('filt on not listed')

               if name:
                    ndf = ndf[(ndf['User Name'] == name)]
                    context['df'] = ndf
               if firm:
                    ndf = ndf[ndf['Firm Name'] == firm]
               if year:
                    year = int(year)
                    ndf = ndf[(ndf['Year'] == year)]
                    context['df'] = ndf
               if month:
                    ndf = ndf[(ndf['Month'] == month)]
                    context['df'] = ndf
               if name and year:
                    year = int(year)
                    ndf = ndf[(ndf['User Name'] == name) & (ndf['Year'] == year)]
                    context['df'] = ndf
               if name and year and month:
                    year = int(year)
                    ndf = ndf[(ndf['User Name'] == name) & (ndf['Year'] == year) & (ndf['Month'] == month)]
                    context['df'] = ndf
               if name and year and month and firm:
                    year = int(year)
                    ndf = ndf[(ndf['User Name'] == name) & (ndf['Year'] == year) & (ndf['Month'] == month) & (ndf['Firm Name'])]
                    context['df'] = ndf
               else:
                    context['df'] = ndf

               #for showing number of rows of filtered  data
               rows, columns = context['df'].shape
               record_spelling = ''
               if rows == 1 or rows == 0:
                    record_spelling = 'record'
               else: 
                    record_spelling = 'records'
               context['records_found'] = f'{rows} {record_spelling} found'

               #final data filtration with comma seperation, adding column to show numb of comp 
               #first-grouping the columns
               grouped_data = ndf.groupby(['User Key', 'User Name','Year', 'Month'])[['Firm Name', 'Company Name', 'Listed']].agg(concatenate_with_seperator)

               grouped_data = grouped_data.reset_index()

               #function for counting any cell value passed as series
               cell_value = 0
               def count_cell_values(df_column):
                    return df_column.str.count(', ')+1
               
               
               num_of_companies = count_cell_values(grouped_data['Company Name'])
               grouped_data['num_of_companies'] = num_of_companies


               context['df'] = grouped_data

     #setting limit for displaying whole data so that site doesn't get crashed
     num_of_rows, num_of_columns = context['df'].shape
     if num_of_rows >= 1500:
          context['df'] = context['df'].head(1500)
     else:
          context['df'] = context['df']

     return render(request, 'filter_data.html', context)

def create_plotly_chart_v(data, filter_column):
    chart_data = data[filter_column].value_counts().reset_index()
    chart_data.columns = ['Category', 'Count']
    fig = px.bar(chart_data, x='Count', y='Category', orientation='h', title=filter_column)
    return fig

def visualize_data(request):
    context = {
        'plotly_chart': None
    }
    
    if request.method == "POST":
        if 'industry_chart' in request.POST:
            chart = create_plotly_chart_v(df, 'Business Industry')
            chart_div = chart.to_html(full_html=False, default_height=500)
            context['plotly_chart'] = chart_div

        if 'sector_chart' in request.POST:
            chart = create_plotly_chart_v(df, 'business Sector')
            chart_div = chart.to_html(full_html=False, default_height=500)
            context['plotly_chart'] = chart_div

        if 'legal_status_chart' in request.POST:
            chart = create_plotly_chart_v(df, 'Legal status')
            chart_div = chart.to_html(full_html=False, default_height=500)
            context['plotly_chart'] = chart_div

    return render(request, 'visualize_data.html', context)
     


# Assuming df_only_show is your DataFrame


def create_plotly_chart(request, df, chart_filter=None):
    if chart_filter == 'Legal status':
        # Bar Chart for Legal Status
        legal_status_data = df['Legal status'].value_counts().reset_index()
        legal_status_data.columns = ['Legal status', 'Count']
        fig = px.bar(legal_status_data, x='Legal status', y='Count', title='Legal Status Distribution')
    elif chart_filter == 'business Sector':
        # Pie Chart for Sector Wise
        sector_data = df['business Sector'].value_counts().reset_index()
        sector_data.columns = ['business Sector', 'Count']
        fig = px.pie(sector_data, names='business Sector', values='Count', title='Sector-wise Distribution')
    elif chart_filter == 'Business Industry':
        # Pie Chart for Industry Wise
        industry_data = df['Business Industry'].value_counts().reset_index()
        industry_data.columns = ['Business Industry', 'Count']
        fig = px.pie(industry_data, names='Business Industry', values='Count', title='Industry-wise Distribution')
    else:
          grouped_dataC=[]
          cell_value = 0
          def count_cell_values(df_column):
               return df_column.str.count(', ')+1                     
          num_of_companies = count_cell_values(grouped_data['Company Name'])
          grouped_dataC['num_of_companies'] = num_of_companies
        # Sort the DataFrame by 'Document Date'
          df['Document Date'] = pd.to_datetime(df['Document Date'])  # Ensure 'Document Date' is treated as a date
          df = df.sort_values(by='Document Date')

        # Line Chart for the number of companies for each date
     
          line_data = df.groupby('Document Date')
          line_data.columns = ['Document Date', 'num_of_companies']
          fig = px.line(line_data, x='Document Date', y='num_of_companies', title='Number of Entities Audited per day')


    chart_div = plot(fig, output_type='div', include_plotlyjs=False)
    return chart_div



def admin_dashboard(request):
    # Load or fetch your DataFrame df_only_show here
     df=df_only_show
    # Line Chart for the number of companies for each date
     line_chart = create_plotly_chart(request, df, 'line-chart')

    # Bar Chart for Legal Status
     legal_status_chart = create_plotly_chart(request, df, 'Legal status')

    # Pie Chart for Sector Wise
     sector_chart = create_plotly_chart(request, df, 'business Sector')

    # Pie Chart for Industry Wise
     industry_chart = create_plotly_chart(request, df, 'Business Industry')

    # For showing the latest data
     grouped_data = df.groupby(['User Key', 'User Name', 'Day', 'Month', 'Year'])[['Firm Name', 'Company Name', 'DVC Date']].agg(lambda x: ', '.join(x))
     grouped_data = grouped_data.reset_index()
     latest_date = grouped_data.sort_values(by='DVC Date', ascending=False)

     context = {
        'df': latest_date.head(5),
        'line_chart': line_chart,
        'legal_status_chart': legal_status_chart,
        'sector_chart': sector_chart,
        'industry_chart': industry_chart,
    }

     return render(request, 'admin_dashboard.html', context)

