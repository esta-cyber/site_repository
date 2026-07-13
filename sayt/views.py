from datetime import timedelta
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone
from django.contrib import messages
from .models import Person, PointAward, TokenAward

USERS = [
    {'surname': 'Adminov', 'login': 'admin', 'role': 'admin', 'group': ''},
    {'surname': 'Teacher1', 'login': 'teacher1', 'role': 'teacher', 'group': 'guruh1'},
    {'surname': 'Teacher2', 'login': 'teacher2', 'role': 'teacher', 'group': 'guruh2'},
    {'surname': 'Teacher3', 'login': 'teacher3', 'role': 'teacher', 'group': 'guruh3'},
]

for group_index in range(1, 4):
    for student_index in range(1, 16):
        USERS.append({
            'surname': f'Talaba{group_index}_{student_index}',
            'login': f'talaba{group_index}_{student_index}',
            'role': 'student',
            'group': f'guruh{group_index}',
        })

# --------------------------------------------------------------------------------------------

def enter(request):
    error_message = None
    saved_surname = request.COOKIES.get('saved_surname', '')
    saved_login = request.COOKIES.get('saved_login', '')

    person_id = request.session.get('person_id')
    if person_id:
        current_person = Person.objects.filter(id=person_id).first()
        if current_person:
            if current_person.role == 'admin':
                return redirect('admin_bulimi')
            elif current_person.role == 'teacher':
                return redirect('teacher_bulimi')
            else:
                return redirect('uquvchi_bulimi')

    if request.method == 'POST':
        surname = request.POST.get('surname', '').strip()
        login = request.POST.get('login', '').strip()

        person = Person.objects.filter(surname=surname, login=login).first()

        if not person:
            static_user = next((u for u in USERS if u['surname'] == surname and u['login'] == login), None)
            if static_user:
                person = Person.objects.create(
                    surname=static_user['surname'],
                    login=static_user['login'],
                    role=static_user['role'],
                    group=static_user.get('group', ''),
                )

        if person:
            request.session['person_id'] = person.id
            
            if person.role == 'admin':
                response = redirect('admin_bulimi')
            elif person.role == 'teacher':
                response = redirect('teacher_bulimi')
            else:
                response = redirect('uquvchi_bulimi')

            response.set_cookie('saved_surname', surname, max_age=30 * 24 * 60 * 60)
            response.set_cookie('saved_login', login, max_age=30 * 24 * 60 * 60)
            return response
        else:
            error_message = "Noto'g'ri familiya yoki login"

    return render(request, 'enter.html', {
        'error_message': error_message,
        'saved_surname': saved_surname,
        'saved_login': saved_login,
    })

# -------------------------------------------------------------------------------

def logout_view(request):
    request.session.flush()
    return redirect('enter')

# --------------------------------------------------------------------------------

def admin_boshqaruv_bulimi(request):
    person_id = request.session.get('person_id')
    if not person_id:
        return redirect('enter')
        
    user = Person.objects.filter(id=person_id).first()
    if user is None or user.role != Person.ROLE_ADMIN:
        return redirect('enter')

    edit_user = None
    
    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        user_id = request.POST.get('user_id')
        
        if action == 'delete' and user_id:
            person_to_delete = Person.objects.filter(id=user_id).first()
            if person_to_delete:
                person_to_delete.delete()
                messages.success(request, 'Foydalanuvchi muvaffaqiyatli o‘chirildi.')
            else:
                messages.error(request, 'Foydalanuvchi topilmadi.')
            return redirect('admin_bulimi')
            
        elif action == 'delete_group_global':
            group_to_delete = request.POST.get('group_name', '').strip()
            if group_to_delete:
                students_in_group = Person.objects.filter(group=group_to_delete)
                for member in students_in_group:
                    member.group = ""
                    member.save()
                
                teachers = Person.objects.filter(role=Person.ROLE_TEACHER)
                for t in teachers:
                    if t.group:
                        g_list = [g.strip() for g in t.group.split(',') if g.strip()]
                        if group_to_delete in g_list:
                            g_list.remove(group_to_delete)
                            t.group = ", ".join(g_list)
                            t.save()
                            
                messages.success(request, f"'{group_to_delete}' guruhi tizimdan butunlay o'chirildi (Foydalanuvchilar guruhdan chiqarildi).")
            return redirect('admin_bulimi')

        else:
            surname = request.POST.get('surname', '').strip()
            login = request.POST.get('login', '').strip()
            role = request.POST.get('role', '')
            group = request.POST.get('group', '').strip()
            class_name = request.POST.get('class_name', '').strip()
            student_id = request.POST.get('student_id', '').strip()
            phone = request.POST.get('phone', '').strip()
            email = request.POST.get('email', '').strip()
            parent_name = request.POST.get('parent_name', '').strip()
            birthday = request.POST.get('birthday', '').strip()
            address = request.POST.get('address', '').strip()

            if user_id:
                edit_user = Person.objects.filter(id=user_id).first()

            if surname and login and role in [Person.ROLE_ADMIN, Person.ROLE_TEACHER, Person.ROLE_STUDENT]:
                if edit_user:
                    if Person.objects.filter(login=login).exclude(id=edit_user.id).exists():
                        messages.error(request, 'Bu login avvaldan mavjud.')
                    else:
                        edit_user.surname = surname
                        edit_user.login = login
                        edit_user.role = role
                        edit_user.group = group
                        edit_user.class_name = class_name
                        edit_user.student_id = student_id
                        edit_user.phone = phone
                        edit_user.email = email
                        edit_user.parent_name = parent_name
                        edit_user.birthday = birthday or None
                        edit_user.address = address
                        edit_user.save()
                        messages.success(request, 'Foydalanuvchi ma’lumotlari yangilandi.')
                        return redirect('admin_bulimi')
                else:
                    if Person.objects.filter(login=login).exists():
                        messages.error(request, 'Bu login avvaldan mavjud.')
                    else:
                        Person.objects.create(
                            surname=surname, login=login, role=role, group=group,
                            class_name=class_name, student_id=student_id, phone=phone,
                            email=email, parent_name=parent_name, birthday=birthday or None,
                            address=address
                        )
                        messages.success(request, 'Yangi foydalanuvchi qo‘shildi.')
                        return redirect('admin_bulimi')
            else:
                messages.error(request, 'Toʻliq maʼlumot kiriting.')

    edit_id = request.GET.get('edit_id')
    if edit_id:
        edit_user = Person.objects.filter(id=edit_id).first()

    all_people = Person.objects.all()
    existing_groups = set()
    for p in all_people:
        if p.group:
            parts = [g.strip() for g in p.group.split(',') if g.strip()]
            for part in parts:
                existing_groups.add(part)

    people = Person.objects.order_by('role', 'group', 'surname')
    
    return render(request, 'admin_dashboard.html', {
        'user': user,
        'people': people,
        'edit_user': edit_user,
        'existing_groups': sorted(list(existing_groups)),
    })

# -----------------------------------------------------------------------------------

def teacher_boshqaruv_bulimi(request):
    person_id = request.session.get('person_id')
    if not person_id:
        return redirect('enter')
        
    teacher = Person.objects.filter(id=person_id).first()
    if teacher is None or teacher.role != Person.ROLE_TEACHER:
        return redirect('enter')

    today = timezone.localdate()

    teacher_groups = [g.strip() for g in teacher.group.split(',') if g.strip()]
    if not teacher_groups and teacher.group:
        teacher_groups = [teacher.group]

    if request.method == 'POST' and request.POST.get('action') == 'add_group':
        new_group_name = request.POST.get('new_group', '').strip()
        if new_group_name:
            if teacher.group:
                teacher.group = f"{teacher.group}, {new_group_name}"
            else:
                teacher.group = new_group_name
            teacher.save()
            messages.success(request, f"Yangi {new_group_name} muvaffaqiyatli qo'shildi.")
            return redirect('teacher_bulimi')

    selected_group = request.GET.get('group')
    
    students = None
    group_tokens_today = 0
    remaining_tokens = 10
    students_awarded_today = 0

    if selected_group:
        students = Person.objects.filter(role=Person.ROLE_STUDENT, group=selected_group).order_by('surname')
        group_tokens_today = TokenAward.objects.filter(student__group=selected_group, created_at__date=today).count()
        remaining_tokens = max(0, 10 - group_tokens_today)
        students_awarded_today = PointAward.objects.filter(teacher=teacher, created_at__date=today, student__group=selected_group).values('student').distinct().count()

        if request.method == 'POST':
            action = request.POST.get('action')
            student_id = request.POST.get('student_id')
            student = Person.objects.filter(id=student_id, role=Person.ROLE_STUDENT, group=selected_group).first()

            if student:
                if action == 'give_points':
                    already_awarded = PointAward.objects.filter(student=student, created_at__date=today).exists()
                    if already_awarded:
                        messages.error(request, 'Bugun ushbu talabaga allaqachon ball berilgan.')
                    else:
                        try:
                            amount = int(request.POST.get('amount', '1'))
                        except ValueError:
                            amount = 1
                        if 1 <= amount <= 50:
                            PointAward.objects.create(teacher=teacher, student=student, amount=amount)
                            messages.success(request, f"{student.surname}ga {amount} ball berildi.")
                        else:
                            messages.error(request, '1 dan 50 gacha ball kiriting.')
                    return redirect(f"{request.path}?group={selected_group}")

                elif action == 'give_token':
                    already_token = TokenAward.objects.filter(student=student, created_at__date=today).exists()
                    if already_token:
                        messages.error(request, 'Bugun ushbu talabaga star berilgan.')
                    elif group_tokens_today >= 10:
                        messages.error(request, 'Bugun guruh limiti tugadi (10/10).')
                    else:
                        TokenAward.objects.create(teacher=teacher, student=student)
                        messages.success(request, f"{student.surname}ga Star (Token) berildi.")
                    return redirect(f"{request.path}?group={selected_group}")

    students_data = []
    if students:
        for s in students:
            students_data.append({
                'id': s.id,
                'surname': s.surname,
                'total_points': s.total_points(),
                'total_tokens': s.total_tokens(),
                'has_points_today': PointAward.objects.filter(student=s, created_at__date=today).exists(),
                'has_token_today': TokenAward.objects.filter(student=s, created_at__date=today).exists(),
            })

    context = {
        'teacher': teacher,
        'teacher_groups': teacher_groups,
        'selected_group': selected_group,
        'students': students_data,
        'students_awarded_today': students_awarded_today,
        'students_count': students.count() if students else 0,
        'group_tokens_today': group_tokens_today,
        'remaining_tokens': remaining_tokens,
    }
    return render(request, 'teacher_dashboard.html', context)

# -----------------------------------------------------------------------------------

def uquvchining_bulimi(request):
    person_id = request.session.get('person_id')
    if not person_id:
        return redirect('enter')
        
    student = Person.objects.filter(id=person_id).first()
    if student is None or student.role != Person.ROLE_STUDENT:
        return redirect('enter')

    points = student.total_points()
    token_total = student.total_tokens()

    context = {
        'student': {
            'name': student.surname,
            'points': points,
            'token_total': token_total,
        },
    }
    return render(request, 'uquvchining_bulimi.html', context)

# -------------------------------------------------------------------------------

def store_page(request):
    person_id = request.session.get('person_id')
    if not person_id:
        return redirect('enter')
        
    student = Person.objects.filter(id=person_id).first()
    if student is None or student.role != Person.ROLE_STUDENT:
        return redirect('enter')

    return render(request, 'store.html', {'student': student})

# --------------------------------------------------------------------------------

def chat_page(request):
    person_id = request.session.get('person_id')
    if not person_id:
        return redirect('enter')
        
    user = Person.objects.filter(id=person_id).first()
    if user is None:
        return redirect('enter')

    return render(request, 'chat.html', {'user': user})

