from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import csv, math
from collections import defaultdict
from.models import Expense

def dashboard(request):
    return render(request, 'finance_module/finance.html')

def clean_priority(raw):
    v = str(raw or '').strip().capitalize()
    return v if v in ['High','Medium','Low'] else 'Medium'

@api_view(['GET'])
def expense_list(request):
    limit = int(request.GET.get('limit', 300))
    qs = Expense.objects.all().order_by('-expense_id')[:limit]
    return Response([{
        'expense_id': e.expense_id,
        'department': e.department,
        'category': e.category,
        'amount': float(e.amount or 0),
        'budget_used': float(e.budget_used or 0),
        'budget_allocated': float(e.budget_allocated or e.amount or 0),
        'vendor_name': e.vendor_name,
        'vendor': e.vendor_name,
        'payment_method': e.payment_method,
        'expense_date': str(e.expense_date)[:10] if e.expense_date else '2024-01-01',
        'expense_priority': clean_priority(e.expense_priority),
        'priority': clean_priority(e.expense_priority),
        'approval_status': e.approval_status or 'Pending',
    } for e in qs])

@api_view(['GET'])
def budget_list(request):
    qs = Expense.objects.all().order_by('-expense_id')[:300] 
    return Response([{
        'department': e.department,
        'category': e.category,
        'limit_amount': round(float(e.budget_allocated or e.amount or 100000),2),
        'used_amount': round(float(e.budget_used or 0),2),
        'percent': round((float(e.budget_used or 0)/float(e.budget_allocated or 1)*100),1) if e.budget_allocated else 0,
        'priority': clean_priority(e.expense_priority),
    } for e in qs])

@api_view(['GET'])
def invoice_list(request):
    qs = Expense.objects.all().order_by('-expense_id')[:150] 
    return Response([{
        'invoice_number': f"INV{e.expense_id}",
        'department': e.department,
        'vendor_name': e.vendor_name,
        'vendor': e.vendor_name,
        'amount': float(e.budget_used or e.amount or 0),
        'status': 'Paid' if e.approval_status=='Approved' else 'pending',
        'expense_date': str(e.expense_date)[:10] if e.expense_date else '2024-01-01',
    } for e in qs])

@api_view(['GET'])
def detailed_reports(request):
    qs = Expense.objects.all()[:1000]
    if not qs.exists():
        return Response({
            'summary':{'total_budget':0,'total_spent':0,'remaining':0,'total_expenses':0,'approved':0,'pending':0,'rejected':0,'utilization':0},
            'by_department':[],'by_category':[],'by_priority':[],'monthly':[],'top_vendors':[]
        })
    total_spent=total_alloc=0
    by_dept={}; dept_alloc={}; by_cat={}; cat_alloc={}; by_prio={'High':0,'Medium':0,'Low':0}
    monthly={}; vendors={}; a=p=r=0
    for e in qs:
        used=float(e.budget_used or e.amount or 0)
        alloc=float(e.budget_allocated or e.amount or 0) or 1
        total_spent+=used
        total_alloc+=alloc
        by_dept[e.department]=by_dept.get(e.department,0)+used
        dept_alloc[e.department]=dept_alloc.get(e.department,0)+alloc
        by_cat[e.category]=by_cat.get(e.category,0)+used
        cat_alloc[e.category]=cat_alloc.get(e.category,0)+alloc
        by_prio[clean_priority(e.expense_priority)]=by_prio.get(clean_priority(e.expense_priority),0)+used
        vendors[e.vendor_name]=vendors.get(e.vendor_name,0)+used
        m=str(e.expense_date)[:7]
        if len(m)==7: monthly[m]=monthly.get(m,0)+used
        if e.approval_status=='Approved': a+=1
        elif e.approval_status=='Rejected': r+=1
        else: p+=1
    util=round(total_spent/total_alloc*100,1) if total_alloc else 0
    return Response({
        'summary':{'total_budget':round(total_alloc,2),'total_spent':round(total_spent,2),'remaining':round(total_alloc-total_spent,2),'total_expenses':qs.count(),'approved':a,'pending':p,'rejected':r,'utilization':util,'util_percent':util},
        'by_department':[{'department':k,'total':round(v,2),'budget':round(dept_alloc.get(k,0),2),'percent':round(v/total_spent*100,1) if total_spent else 0,'variance':round((v-dept_alloc.get(k,0))/dept_alloc.get(k,0)*100,1) if dept_alloc.get(k,0) else 0} for k,v in sorted(by_dept.items(),key=lambda x:x[1],reverse=True)],
        'by_category':[{'category':k,'total':round(v,2),'budget':round(cat_alloc.get(k,0),2),'variance':round((v-cat_alloc.get(k,0))/cat_alloc.get(k,0)*100,1) if cat_alloc.get(k,0) else 0} for k,v in sorted(by_cat.items(),key=lambda x:x[1],reverse=True)],
        'by_priority':[{'priority':k,'total':round(v,2)} for k,v in by_prio.items() if v>0],
        'monthly':[{'month':k,'total':round(v,2)} for k,v in sorted(monthly.items())],
        'top_vendors':[{'vendor':k,'total':round(v,2)} for k,v in sorted(vendors.items(),key=lambda x:x[1],reverse=True)[:5]],
    })

@api_view(['GET'])
def anomaly_detection(request):
    qs = Expense.objects.all()[:1000]
    if not qs.exists():
        return Response({'anomalies':[], 'summary':{'total':0,'high':0,'medium':0,'low':0,'total_checked':0}})
    dept_amounts=defaultdict(list)
    for e in qs: dept_amounts[e.department].append(float(e.budget_used or e.amount or 0))
    dept_stats={}
    for dept, vals in dept_amounts.items():
        vs=sorted(vals); n=len(vs)
        mean=sum(vs)/n if n else 0
        var=sum((x-mean)**2 for x in vs)/n if n else 0
        std=math.sqrt(var) if var else 0
        q1=vs[n//4] if n>=4 else vs[0]
        q3=vs[3*n//4] if n>=4 else vs[-1]
        iqr=q3-q1
        dept_stats[dept]={'mean':mean,'std':std,'upper':q3+1.5*iqr if iqr else q3*1.5}

    anomalies=[]; seen={}
    for e in qs:
        used=float(e.budget_used or e.amount or 0)
        alloc=float(e.budget_allocated or e.amount or 1) or 1
        stats=dept_stats.get(e.department)
        reasons=[]; score=0; severity='Low'
        if stats and stats['std']>0:
            z=abs((used-stats['mean'])/stats['std'])
            if z>3:
                reasons.append(f"🔴 Very High: ₹{used:,.0f} is {z:.1f}σ above {e.department} avg ₹{stats['mean']:,.0f}")
                score+=z; severity='High'
            elif z>2:
                reasons.append(f"🟡 High: ₹{used:,.0f} vs avg ₹{stats['mean']:,.0f}")
                score+=z; severity='Medium' if severity=='Low' else severity
        if stats and used>stats['upper']:
            reasons.append(f"📦 Unusual: ₹{used:,.0f} > normal max ₹{stats['upper']:,.0f}")
            score+=2
        if used>alloc:
            over=(used-alloc)/alloc*100
            reasons.append(f"💸 Over Budget {over:.0f}%: Used ₹{used:,.0f} > Budget ₹{alloc:,.0f}")
            score+=over/40
            severity='High' if over>30 else 'Medium'
        key=f"{e.vendor_name}-{used}"
        seen[key]=seen.get(key,0)+1
        if seen[key]>2:
            reasons.append(f"🔁 Duplicate x{seen[key]}: {e.vendor_name}")
            score+=1

        if reasons:
            anomalies.append({
                'expense_id': e.expense_id,
                'department': e.department,
                'category': e.category,
                'budget': round(alloc,2),
                'used': round(used,2),
                'amount': round(used,2),
                'allocated': round(alloc,2),
                'vendor': e.vendor_name,
                'expense_date': str(e.expense_date)[:10] if e.expense_date else '2024-01-01',
                'priority': clean_priority(e.expense_priority),
                'reason_text': ' • '.join(reasons),
                'score': round(score,2),
                'severity': severity
            })
    anomalies.sort(key=lambda x: (3 if x['severity']=='High' else 2 if x['severity']=='Medium' else 1, x['score']), reverse=True)
    return Response({
        'anomalies':anomalies[:200],
        'summary':{
            'total':len(anomalies),
            'high':len([a for a in anomalies if a['severity']=='High']),
            'medium':len([a for a in anomalies if a['severity']=='Medium']),
            'low':len([a for a in anomalies if a['severity']=='Low']),
            'total_checked':qs.count()
        }
    })

@csrf_exempt
@api_view(['POST'])
def import_csv_upload(request):
    f=request.FILES.get('file')
    if not f: return Response({'message':'No file','count':0}, status=400)
    Expense.objects.all().delete()
    text=f.read().decode('utf-8',errors='ignore').splitlines()
    reader=csv.DictReader(text)
    objs=[]; count=0
    for row in reader:
        if count>=1000: break
        prio=clean_priority(row.get('expense_priority') or row.get('priority'))
        try: alloc=float(row.get('budget_allocated') or 0)
        except: alloc=0
        try: used=float(row.get('budget_used') or row.get('amount') or 0)
        except: used=0
        try: amt=float(row.get('amount') or used or 0)
        except: amt=0
        if alloc==0: alloc=amt or (used*2.08 if used else 100000)

        raw_date = (row.get('expense_date') or '2024-01-01')[:10]

        objs.append(Expense(
            expense_id=(row.get('expense_id') or f"EXP{1000+count}").strip(),
            department=(row.get('department') or 'General').strip()[:100],
            category=(row.get('category') or 'General').strip()[:100],
            amount=amt,
            budget_used=used,
            budget_allocated=alloc,
            budget_limit=alloc,
            vendor_name=(row.get('vendor_name') or 'N/A')[:200],
            payment_method=(row.get('payment_method') or 'Cash')[:50],
            expense_date=raw_date,
            expense_priority=prio,
            approval_status=(row.get('approval_status') or 'Pending')[:20]
        ))
        count+=1
        if len(objs)>=300:
            Expense.objects.bulk_create(objs, ignore_conflicts=True)
            objs=[]
    if objs: Expense.objects.bulk_create(objs, ignore_conflicts=True)
    return Response({'message':f'✅ Imported {count}','count':count})

@csrf_exempt
@api_view(['POST'])
def approve_expense(request, expense_id):
    Expense.objects.filter(expense_id=expense_id).update(approval_status='Approved')
    return Response({'message':'Approved'})

@csrf_exempt
@api_view(['POST'])
def reject_expense(request, expense_id):
    Expense.objects.filter(expense_id=expense_id).update(approval_status='Rejected')
    return Response({'message':'Rejected'})

@csrf_exempt
@api_view(['POST'])
def pay_invoice(request, invoice_number):
    eid=invoice_number.replace('INV','')
    Expense.objects.filter(expense_id=eid).update(approval_status='Approved')
    return Response({'message':f'✅ {invoice_number} Paid!'})

@csrf_exempt
@api_view(['POST','PUT'])
def update_budget_limit(request):
    dept=request.data.get('department')
    cat=request.data.get('category')
    lim=float(request.data.get('limit_amount') or 0)
    if lim<=0:
        return Response({'message':'Invalid limit'}, status=400)
    Expense.objects.filter(department=dept, category=cat).update(budget_allocated=lim, budget_limit=lim, amount=lim)
    return Response({'message':'Updated','limit':lim})

@csrf_exempt
@api_view(['POST','GET'])
def clear_all(request):
    Expense.objects.all().delete()
    return Response({'message':'Cleared'})