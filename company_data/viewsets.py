from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Company
import zipfile
import logging
from .data_processing import process_xml, save_companies_to_db, download_and_temp_save


class CompanyDataViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_path="download_file")
    def update_company_info(self, request):
        logging.info("Starting file download process...")
        url1 = request.GET.get('url1', 'https://report.financnasprava.sk/ds_dphs.zip')
        url2 = request.GET.get('url2', 'https://report.financnasprava.sk/ds_dsrdp.zip')
        companies_dict = {}
        try:
            content1, err1 = download_and_temp_save(url1)
            content2, err2 = download_and_temp_save(url2)

            if err1 or err2:
                return Response({'error_data': f'{err1} {err2}'.strip()}, status=status.HTTP_400_BAD_REQUEST)
            with zipfile.ZipFile(content1, 'r') as zip_file1:
                process_xml(zip_file1, companies_dict)
            with zipfile.ZipFile(content2, 'r') as zip_file2:
                process_xml(zip_file2, companies_dict)
            save_companies_to_db(companies_dict)
            return Response({'message': 'Successfully downloaded and processed ZIP files'})
        except zipfile.BadZipFile:
            return Response({'error': 'The provided file is not a valid ZIP file.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path="data_control")
    def data_control(self, request):
        try:
            crn = request.data.get("crn")
            tax_id = request.data.get("tax_id")
            vat_id = request.data.get("vat_id")

            if not any([crn, tax_id, vat_id]):
                return Response({"crn": '', "tax_id": '', "vat_id": ''}, status=status.HTTP_200_OK)

            company = None
            error_message = None

            if crn:
                company = Company.objects.filter(crn=crn).first()
                if not company and not tax_id and not vat_id:
                    error_message = "Invalid crn"

            if not company and tax_id:
                company = Company.objects.filter(tax_id=tax_id).first()
                if not company and not vat_id:
                    error_message = "Invalid tax_id"

            if not company and vat_id:
                company = Company.objects.filter(vat_id=vat_id).first()
                if not company:
                    error_message = "Invalid vat_id"

            if not company:
                return Response({"message": error_message or "No valid identifiers provided"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "crn": company.crn,
                "tax_id": company.tax_id,
                "vat_id": company.vat_id,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": f"An error occurred: {e}"}, status=status.HTTP_400_BAD_REQUEST)

