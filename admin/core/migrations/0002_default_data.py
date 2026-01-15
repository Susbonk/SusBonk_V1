from django.db import migrations


def load_default_data(apps, schema_editor):
    Prompt = apps.get_model('core', 'Prompt')
    RuntimeStatistics = apps.get_model('core', 'RuntimeStatistics')
    
    # Create default prompts
    prompts = [
        {
            'name': 'crypto_scam',
            'prompt_text': 'Analyze this message for cryptocurrency scams, pump-and-dump schemes, fake investment opportunities, or suspicious financial promises. Look for urgency tactics, unrealistic returns, or pressure to invest quickly.'
        },
        {
            'name': 'spam_links',
            'prompt_text': 'Check if this message contains spam links, phishing attempts, or suspicious URLs. Look for shortened links, suspicious domains, or messages designed to trick users into clicking.'
        },
        {
            'name': 'adult_content',
            'prompt_text': 'Determine if this message contains adult content, sexual material, or NSFW content that would be inappropriate for a general audience.'
        },
        {
            'name': 'harassment',
            'prompt_text': 'Analyze this message for harassment, bullying, hate speech, or toxic behavior directed at individuals or groups.'
        },
        {
            'name': 'commercial_spam',
            'prompt_text': 'Check if this message is commercial spam, unwanted advertising, or promotional content that disrupts normal conversation flow.'
        },
    ]
    
    for prompt_data in prompts:
        Prompt.objects.get_or_create(name=prompt_data['name'], defaults=prompt_data)
    
    # Create default runtime statistics
    RuntimeStatistics.objects.get_or_create(name='default_stats')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_default_data, reverse_code=migrations.RunPython.noop),
    ]
