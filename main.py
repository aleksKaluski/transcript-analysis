from source import standardisation as sd
import os

# os.chdir(r"C:\data")
print(f"working path: {os.getcwd()}")

sd.standardise(input_folder=r'files\CSV',
               output_folder=r'files\CSV_standardised')


sd.export_folder_to_txt(input_folder=r'files\CSV_standardised',
                        output_folder=r'files\TXT')

sd.export_folder_to_pdf(input_folder=r'files\TXT',
                        output_folder=r'files\PDF')
