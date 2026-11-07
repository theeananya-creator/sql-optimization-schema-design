import json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
R=json.load(open('results/results.json'))
NAVY='#1F3A5F'; TEAL='#2A9D8F'; RED='#C8553D'; GREY='#F3F5F8'

def table(ax,x,y,w,title,cols,hdr=NAVY,rh=0.32):
    h=rh*(len(cols)+1)
    ax.add_patch(Rectangle((x,y-h),w,h,fc='white',ec=hdr,lw=1.6,zorder=2))
    ax.add_patch(Rectangle((x,y-rh),w,rh,fc=hdr,ec=hdr,zorder=3))
    ax.text(x+w/2,y-rh/2,title,color='white',ha='center',va='center',fontsize=10,fontweight='bold',zorder=4)
    for i,(n,t,k) in enumerate(cols):
        yy=y-rh*(i+1.5)
        col={'PK':'#B8860B','FK':TEAL,'':'#222'}[k]
        ax.text(x+0.1,yy,(k+' ' if k else '   ')+n,fontsize=8.5,va='center',color=col,fontweight='bold' if k else 'normal',zorder=4)
        ax.text(x+w-0.1,yy,t,fontsize=8,va='center',ha='right',color='#666',zorder=4)
    return dict(x=x,y=y,w=w,h=h,rh=rh)

# BEFORE
fig,ax=plt.subplots(figsize=(7,5.2)); ax.set_xlim(0,7); ax.set_ylim(0,5.2); ax.axis('off')
cols=[('row_id','INTEGER','PK'),('order_id','INTEGER',''),('order_date','TEXT',''),('customer_name','TEXT',''),('customer_email','TEXT',''),
('customer_phone','TEXT',''),('customer_city','TEXT',''),('product_name','TEXT',''),('category_name','TEXT',''),('unit_price','REAL',''),
('quantity','INTEGER',''),('order_status','TEXT',''),('payment_method','TEXT','')]
table(ax,1.6,4.9,3.8,'orders_flat  (legacy)',cols,hdr=RED)
ax.text(5.6,3.4,'Customer, product and\ncategory data repeated on\nevery order line (~300k rows)',fontsize=9,color=RED,va='center')
ax.text(0.05,0.15,'Single wide table: no foreign keys, no secondary indexes, update/insert/delete anomalies',fontsize=8.5,style='italic',color='#444')
plt.savefig('docs/images/schema_before.png',dpi=170,bbox_inches='tight'); plt.close()

# AFTER
fig,ax=plt.subplots(figsize=(10.5,7.2)); ax.set_xlim(0,10.5); ax.set_ylim(-0.9,6.4); ax.axis('off')
cust=table(ax,0.2,6.2,2.9,'customers',[('customer_id','INT','PK'),('full_name','TEXT',''),('email','TEXT  UNIQUE',''),('phone','TEXT',''),('city','TEXT','')],hdr=NAVY)
orde=table(ax,3.9,6.2,3.0,'orders',[('order_id','INT','PK'),('customer_id','INT','FK'),('order_date','DATE',''),('status','TEXT',''),('payment_method','TEXT',''),('total_amount','DECIMAL','')],hdr=NAVY)
item=table(ax,3.9,3.4,3.0,'order_items',[('order_item_id','INT','PK'),('order_id','INT','FK'),('product_id','INT','FK'),('quantity','INT',''),('unit_price','DECIMAL','')],hdr=TEAL)
prod=table(ax,7.6,3.4,2.8,'products',[('product_id','INT','PK'),('name','TEXT',''),('category_id','INT','FK'),('unit_price','DECIMAL','')],hdr=NAVY)
cat=table(ax,7.6,1.4,2.8,'categories',[('category_id','INT','PK'),('name','TEXT  UNIQUE','')],hdr=NAVY)
def arrow(x1,y1,x2,y2,l1='1',l2='N'):
    ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='-',color='#444',lw=1.4),zorder=1)
    ax.text(x1+0.05*(1 if x2>x1 else -1),y1+0.12,l1,fontsize=9,fontweight='bold',color='#444')
    ax.text(x2-0.2*(1 if x2>x1 else -1),y2+0.12,l2,fontsize=9,fontweight='bold',color='#444')
arrow(3.1,5.3,3.9,5.1)            # customers -> orders
arrow(5.4,6.2-0.32*7,5.4,3.4,'1','N')   # orders -> items
arrow(6.9,2.85,7.6,2.85,'N','1')  # items N -- 1 products
arrow(9.0,3.4-0.32*5,9.0,1.4,'N','1')   # categories -> products (reverse: category 1, products N)
ax.text(0.2,-0.35,'Indexes (beyond PKs):  ux_customers_email (email)   ix_orders_customer (customer_id, total_amount)   ix_orders_date (order_date, order_id)\n'
 'ix_orders_date_amt (order_date, total_amount)   ix_items_order (order_id)   ix_items_product (product_id)',fontsize=8,color='#333')
ax.text(0.2,-0.8,'PK = primary key   FK = foreign key   1 / N = cardinality',fontsize=8,style='italic',color='#555')
plt.savefig('docs/images/erd_after.png',dpi=170,bbox_inches='tight'); plt.close()

# PERF
import numpy as np
qs=R['queries']; labels=[q['name'].split(' ')[0]+'\n'+' '.join(q['name'].split(' ')[1:]) for q in qs]
bad=[q['t_bad'] for q in qs]; good=[q['t_good'] for q in qs]
fig,ax=plt.subplots(figsize=(8.5,4.6)); x=np.arange(len(qs)); w=0.36
b1=ax.bar(x-w/2,bad,w,color=RED,label='Original (flat table, no indexes)')
b2=ax.bar(x+w/2,good,w,color=TEAL,label='Optimized (normalized + indexes)')
ax.set_yscale('log'); ax.set_ylabel('Median execution time (ms, log scale)'); ax.set_xticks(x); ax.set_xticklabels(labels,fontsize=8.5)
for r,v in list(zip(b1,bad))+list(zip(b2,good)): ax.text(r.get_x()+r.get_width()/2,v*1.12,f'{v:g}',ha='center',fontsize=8.5)
ax.set_ylim(0.002,2500); ax.legend(frameon=False,fontsize=9); ax.spines[['top','right']].set_visible(False)
ax.set_title('Query execution time: before vs. after',fontsize=11,fontweight='bold')
plt.tight_layout(); plt.savefig('docs/images/perf.png',dpi=170); plt.close()

# SPEEDUP + storage
fig,(a1,a2)=plt.subplots(1,2,figsize=(8.5,3.6),gridspec_kw={'width_ratios':[1.6,1]})
sp=[b/g for b,g in zip(bad,good)]
a1.barh([q['name'].split(' ')[0] for q in qs][::-1],sp[::-1],color=NAVY)
for i,v in enumerate(sp[::-1]): a1.text(v*1.03,i,f'{v:,.0f}x',va='center',fontsize=9)
a1.set_xscale('log'); a1.set_xlim(1,sp[0]*6 if max(sp)==sp[0] else max(sp)*6); a1.set_xlabel('Speed-up factor (log scale)'); a1.set_title('Speed-up per query',fontsize=10,fontweight='bold')
a1.spines[['top','right']].set_visible(False)
a2.bar(['Flat table','Normalized\n(5 tables)'],[R['size_flat_mb'],R['size_norm_mb']],color=[RED,TEAL])
for i,v in enumerate([R['size_flat_mb'],R['size_norm_mb']]): a2.text(i,v+0.8,f'{v} MB',ha='center',fontsize=9)
a2.set_ylabel('Table data size (MB)'); a2.set_title('Storage (tables only)',fontsize=10,fontweight='bold'); a2.spines[['top','right']].set_visible(False)
plt.tight_layout(); plt.savefig('docs/images/speedup.png',dpi=170); plt.close()
