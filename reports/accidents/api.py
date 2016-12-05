import json

import pytz
from time import mktime
from django.views.generic import TemplateView
from django.http import JsonResponse
from reports.accidents.models import *


class JSONResponseMixin(object):
    def render_to_json_response(self, context, **response_kwargs):
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        return context


class APIView(JSONResponseMixin, TemplateView):
    def error(self, message):
        return dict(api_method=self.__class__.__name__, api_status='ERROR', api_message=message)

    def render_to_response(self, context, **response_kwargs):
        if self.request.method == 'GET':
            return self.http_method_not_allowed(self.request)
        return self.render_to_json_response(context, **response_kwargs)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)


class APIDelete(APIView):
    def get_context_data(self, **kwargs):
        body = self.request.body
        try:
            json_request = json.loads(body)
        except ValueError:
            return self.error('Invalid JSON-request syntax')
        if 'id' in json_request:
            try:
                id = int(json_request['id'])
                accident = NAAccident.objects.get(id=id)
                action = 'DELETE'
                accident_dict = {
                    'id': accident.id,
                    'company_ids': [c.id for c in accident.companies.all()],
                    'company_names': [c.name for c in accident.companies.all()],
                    'city_ids': [c.id for c in accident.cities.all()],
                    'city_name': [c.name for c in accident.cities.all()],
                    'start_datetime': mktime(
                        accident.start_datetime.utctimetuple()) if accident.start_datetime else None,
                    'finish_datetime': mktime(
                        accident.finish_datetime.utctimetuple()) if accident.finish_datetime else None,
                    'category_id': accident.category.id if accident.category else None,
                    'category_title': accident.category.title if accident.category else None,
                    'kind_id': accident.kind.id if accident.kind else None,
                    'kind_title': accident.kind.title if accident.kind else None,
                    'locations': accident.locations,
                    'affected_customers': accident.affected_customers,
                    'magistral_customers_affected': accident.magistral_customers_affected,
                    'reason': accident.reason,
                    'actions': accident.actions,
                    'iss_id': accident.iss_id,
                    'consolidation_report_ignore_cause': accident.consolidation_report_ignore_cause
                }
                accident.delete()
                return {
                    'api_method': self.__class__.__name__,
                    'api_status': 'OK',
                    'api_response': accident_dict,
                    'api_action': action}
            except ValueError:
                return self.error('Invalid accident id "{}"'.format(json_request['id']))
            except NAAccident.DoesNotExist:
                return self.error('Accident ID "{}" doesn\'t exist'.format(json_request['id']))
        else:
            return self.error('Invalid request')



class APIGetReferences(APIView):
    def get_context_data(self, **kwargs):
        context = {
            'api_method': self.__class__.__name__,
            'api_status': 'OK',
            'api_response': {
                'cities': {},
                'companies': {},
                'categories': {},
                'kinds': {}}}
        for city in NACity.actives.all():
            context['api_response']['cities'][city.id] = city.name
        for company in NACompany.actives.all():
            context['api_response']['companies'][company.id] = company.name
        for category in NACategory.actives.all():
            context['api_response']['categories'][category.id] = category.number
        for kind in NAKind.actives.all():
            context['api_response']['kinds'][kind.id] = kind.code
        return context


class APIUpdate(APIView):
    def get_context_data(self, **kwargs):
        body = self.request.body

        try:
            json_request = json.loads(body)
        except ValueError:
            return self.error('Invalid JSON-request syntax')

        if 'id' in json_request:
            try:
                id = int(json_request['id'])
                accident = NAAccident.objects.get(id=id)
            except ValueError:
                return self.error('Invalid accident id "{}"'.format(json_request['id']))
            except NAAccident.DoesNotExist:
                return self.error('Accident ID "{}" doesn\'t exist'.format(id))
            action = 'UPDATE'
        else:
            accident = NAAccident(locations=u'', reason=u'', actions=u'')
            accident.save()
            action = 'CREATE'
        save_accident = False

        if 'companies' in json_request:
            try:
                objects = [NACompany.actives.get(id=int(value)) for value in json_request['companies']]
                if accident.companies.count() > 0:
                    accident.companies.clear()
                for c in objects:
                    accident.companies.add(c)
                save_accident = True
            except (ValueError, NACompany.DoesNotExist):
                return self.error('Invalid company ID')

        if 'cities' in json_request:
            try:
                objects = [NACity.actives.get(id=int(value)) for value in json_request['cities']]
                if accident.cities.count() > 0:
                    accident.cities.clear()
                for c in objects:
                    accident.cities.add(c)
                save_accident = True
            except (ValueError, NACity.DoesNotExist):
                return self.error('Invalid city ID')

        try:
            if 'start_datetime' in json_request:
                dt = datetime.fromtimestamp(float(json_request['start_datetime']))
                accident.start_datetime = dt.replace(tzinfo=pytz.UTC)
                save_accident = True

            if 'finish_datetime' in json_request:
                dt = datetime.fromtimestamp(float(json_request['finish_datetime']))
                accident.finish_datetime = dt.replace(tzinfo=pytz.UTC)
                save_accident = True
        except ValueError:
            return self.error("Invalid timestamp")

        if 'category' in json_request:
            try:
                accident.category = NACategory.actives.get(id=int(json_request['category']))
                save_accident = True
            except (ValueError, NACategory.DoesNotExist):
                return self.error('Invalid accident category')

        if 'kind' in json_request:
            try:
                accident.kind = NAKind.actives.get(id=int(json_request['kind']))
                save_accident = True
            except (ValueError, NAKind.DoesNotExist):
                return self.error('Invalid accident kind')

        if 'locations' in json_request:
            try:
                accident.locations = json_request['locations']
                save_accident = True
            except ValueError:
                return self.error('Invalid location list')

        if 'affected_customers' in json_request:
            try:
                accident.affected_customers = int(json_request['affected_customers'])
                save_accident = True
            except ValueError:
                return self.error('Invalid affected customers count')

        if 'magistral_customers_affected' in json_request:
            try:
                accident.magistral_customers_affected = bool(json_request['magistral_customers_affected'])
                save_accident = True
            except ValueError:
                return self.error('Invalid magistral_customers_affected value')

        if 'reason' in json_request:
            try:
                accident.reason = json_request['reason']
                save_accident = True
            except ValueError:
                return self.error('Invalid reason text')

        if 'actions' in json_request:
            try:
                accident.actions = json_request['actions']
                save_accident = True
            except ValueError:
                return self.error('Invalid actions text')

        if 'iss_id' in json_request:
            try:
                accident.iss_id = json_request['iss_id']
                save_accident = True
            except ValueError:
                return self.error('Invalid ISS id')

        if 'consolidation_report_ignore_cause' in json_request:
            try:
                accident.consolidation_report_ignore_cause = json_request['consolidation_report_ignore_cause']
                save_accident = True
            except ValueError:
                return self.error('Invalid consolidation_report_ignore_cause text')

        if save_accident:
            accident.save()
        else:
            if action == 'CREATE':
                accident.delete()
            action = 'LIST'
        if accident.id:
            accident_dict = {
                'id': accident.id,
                'company_ids': [c.id for c in accident.companies.all()],
                'company_names': [c.name for c in accident.companies.all()],
                'city_ids': [c.id for c in accident.cities.all()],
                'city_name': [c.name for c in accident.cities.all()],
                'start_datetime': mktime(accident.start_datetime.utctimetuple()) if accident.start_datetime else None,
                'finish_datetime': mktime(
                    accident.finish_datetime.utctimetuple()) if accident.finish_datetime else None,
                'category_id': accident.category.id if accident.category else None,
                'category_title': accident.category.title if accident.category else None,
                'kind_id': accident.kind.id if accident.kind else None,
                'kind_title': accident.kind.title if accident.kind else None,
                'locations': accident.locations,
                'affected_customers': accident.affected_customers,
                'magistral_customers_affected': accident.magistral_customers_affected,
                'reason': accident.reason,
                'actions': accident.actions,
                'iss_id': accident.iss_id,
                'consolidation_report_ignore_cause': accident.consolidation_report_ignore_cause
            }
            return {
                'api_method': self.__class__.__name__,
                'api_status': 'OK',
                'api_response': accident_dict,
                'api_action': action}
        else:
            return self.error('Invalid API request')
