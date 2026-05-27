import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import ChatSession, ChatMessage, BookRecommendation
from .services import chat_with_assistant, get_book_recommendations
from .forms import RecommendationForm, ChatMessageForm


@login_required
def chat_view(request):
    session = ChatSession.objects.filter(user=request.user).first()
    if not session:
        session = ChatSession.objects.create(user=request.user)

    messages = session.messages.all()
    form = ChatMessageForm()
    return render(request, 'ai_assistant/chat.html', {
        'session': session,
        'messages': messages,
        'form': form,
    })


@login_required
@require_POST
def send_message(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
    except (json.JSONDecodeError, AttributeError):
        user_message = request.POST.get('message', '').strip()

    if not user_message:
        return JsonResponse({'error': 'Порожнє повідомлення'}, status=400)

    session, _ = ChatSession.objects.get_or_create(user=request.user)

    history = [
        {'role': msg.role, 'content': msg.content}
        for msg in session.messages.all()
    ]

    ChatMessage.objects.create(session=session, role='user', content=user_message)

    try:
        ai_response = chat_with_assistant(history, user_message)
        ChatMessage.objects.create(session=session, role='assistant', content=ai_response)
        return JsonResponse({'response': ai_response})
    except Exception as e:
        return JsonResponse({'error': f'Помилка AI: {str(e)}'}, status=500)


@login_required
def recommendations_view(request):
    if request.method == 'POST':
        form = RecommendationForm(request.POST)
        if form.is_valid():
            preferences = form.cleaned_data['preferences']
            try:
                response = get_book_recommendations(preferences)
                BookRecommendation.objects.create(
                    user=request.user,
                    query=preferences,
                    response=response,
                )
                return render(request, 'ai_assistant/recommendations.html', {
                    'form': form,
                    'recommendation': response,
                    'preferences': preferences,
                })
            except Exception as e:
                form.add_error(None, f'Помилка: {str(e)}')
    else:
        form = RecommendationForm()

    past = BookRecommendation.objects.filter(user=request.user)[:5]
    return render(request, 'ai_assistant/recommendations.html', {
        'form': form,
        'past_recommendations': past,
    })


@login_required
def new_chat_session(request):
    ChatSession.objects.filter(user=request.user).delete()
    return redirect('ai_assistant:chat')
