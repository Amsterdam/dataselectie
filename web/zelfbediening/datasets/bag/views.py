# Python
from datetime import date, datetime
import json
# Project 
from datasets.bag import models
from datasets.bag.queries import meta_Q
from datasets.generic.mixins import TableSearchView


class BagSearch(TableSearchView):

    model = models.Nummeraanduiding
    index = 'ZB_BAG'
    q_func = meta_Q

    def elastic_query(self, term, query):
        return meta_Q(term, query)

    def save_context_data(self, response):
        """
        Save the relevant wijk, buurt, ggw and stadsdeel to be used
        later to enrich the results
        """
        self.extra_context_data = {}
        fields = ('buurt_naam', 'buurt_code', 'wijk_code', 'wijk_naam', 'ggw_naam', 'ggw_code', 'stadsdeel_naam', 'stadsdeel_code')
        for item in response['hits']['hits']:
            self.extra_context_data[item['_id']] = {}
            for field in fields:
                self.extra_context_data[item['_id']][field] = item['_source'][field]

    def stringify_item_value(self, value):
        """
        Makes sure that the dict contains only strings for easy jsoning of the dict
        Following actions are taken:
        - None is replace by empty string
        - Boolean is converted to strinf
        - Numbers are converted to string
        - Datetime and Dates are converted to EU norm dates

        Important!
        If no conversion van be found the same value is returned
        This may, or may not break the jsoning of the object list

        @Parameter:
        value - a value to convert to string

        @Returns:
        The string representation of the value
        """
        if (isinstance(value, date) or isinstance(value, datetime)):
            value = value.strftime('%d-%m-%Y')
        elif value is None:
            value = ''
        else:
            # Trying repr, otherwise trying 
            try:
                value = repr(value)
            except:
                try:
                    value = str(value)
                except:
                    pass
        return value

    def update_context_data(self, context):
        # Adding the wijk, ggw, stadsdeel info to the result
        for i in range(len(context['object_list'])):
            # Converting datetime to a eu normal date
            context['object_list'][i].update(
                {k: self.stringify_item_value(v) for k, v in context['object_list'][i].items() if not isinstance(v, str)}
            )
            # Adding the extra context
            context['object_list'][i].update(self.extra_context_data[context['object_list'][i]['id']])
        # Finally serializing the object list
        context['object_list'] = json.dumps(list(context['object_list']))
        return context

