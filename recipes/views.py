from django.shortcuts import render
#to protect class-based view
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView  #to display lists
from .models import Recipe

from .forms import RecipesSearchForm
import pandas as pd
from .utils import get_recipename_from_id, get_chart

      

# Create your views here.

def home(request):
    return render(request, 'recipes/recipes_home.html')


class RecipeListView(LoginRequiredMixin, ListView):           #class-based view
   model = Recipe                         #specify model
   template_name = 'recipes/main.html'    #specify template 

class RecipeDetailView(LoginRequiredMixin, DetailView):                       #class-based view
   model = Recipe                                        #specify model
   template_name = 'recipes/detail.html'                 #specify template


@login_required
def records(request):
   form = RecipesSearchForm(request.POST or None)
   recipe_df = None  # initialize dataframe to None
   recipe_diff = None
   chart = None
   qs = None
    # check if the button is clicked
   if request.method == 'POST':
      recipe_diff = request.POST.get('recipe_diff')  # read recipe_name
      chart_type = request.POST.get('chart_type')  # read recipe chart type

      recipe_diff_data = {"#1": "Easy", "#2": "Medium",
                           "#3": "Intermediate", "#4": "Hard"}
      recipe_diff = recipe_diff_data[recipe_diff]

        # if recipe_diff == '#1':
        #     recipe_diff = 'Easy'
        # if recipe_diff == '#2':
        #     recipe_diff = 'Medium'
        # if recipe_diff == '#3':
        #     recipe_diff = 'Intermediate'
        # if recipe_diff == '#4':
        #     recipe_diff = 'Hard'

      qs = Recipe.objects.all()  # apply filter to extract data
      id_searched = []
      for obj in qs:
         diff = obj.calculate_difficulty()
         if diff == recipe_diff:
            id_searched.append(obj.id)

      qs = qs.filter(id__in=id_searched)
      # qs = Recipe.objects.filter(recipe_name=recipe_diff)

      if qs:  # if data found
            # convert the queryset values to pandas dataframe
         recipe_df = pd.DataFrame(qs.values())

         chart = get_chart(chart_type, recipe_df,
                           labels=recipe_df['name'].values)

         # convert the dataframe to HTML
         recipe_df = recipe_df.to_html()

         for item in qs.values():
            item_id = item["id"]
            item_name = item["name"]
            recipe_df = recipe_df.replace(
               f"<td>{item_name}</td>",
               f'<td><a href = "/recipes/list/{item_id}">{item_name}</td>'
            )

   
    # pack up data to be sent to template in the context dictionary
   context = {
      'form': form,
      'recipe_df': recipe_df,
      'recipe_diff': recipe_diff,
      'chart': chart,
      'qs': qs,
   }
    # load the recipes/records.html page using the data that you just prepared
   return render(request, 'recipes/records.html', context)
