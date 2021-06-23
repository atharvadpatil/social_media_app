from .models import Profile, Relationship

def ProfilePic(request):
    if request.user.is_authenticated:
        profile_obj = Profile.objects.get(user=request.user)
        pic = profile_obj.avatar
        return {
            'picture': pic
        }
    return {}

def invatations_received_no(request):
    if request.user.is_authenticated:
        profile_obj = Profile.objects.get(user=request.user)
        qs_count = Relationship.objects.invitaions_received(profile_obj).count()
        return {'invites_num':qs_count}
    return {} 