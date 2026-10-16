"""Publication figures drawn exclusively from released factual cells and events."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch
from datetime import date
from analyze import ROOT, read_csv, REGION

OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,
 'axes.spines.right':False,'pdf.fonttype':42,'savefig.bbox':'tight'})
COLORS={'AIIB PPM':'#1b5a70','ADB AM':'#d5a34c','EBRD IPAM':'#777b99','WB IPN':'#7e9d86'}
rows=read_csv(ROOT/'data/register_2025.csv')

def save(fig,name):
    fig.savefig(OUT/(name+'.pdf'));fig.savefig(OUT/(name+'.png'),dpi=220);plt.close(fig)

# Exact crosstab; zeros remain visible rather than implied missing observations.
policies=['ADB SPS','EBRD ESP','IFC ESSP & PS','AIIB ESP','AfDB ISP','EIB ESP','WB ESSP','WB ESF','WB PforR Policy','WB DPF Policy']
iams=['AIIB PPM','ADB AM','EBRD IPAM','WB IPN','EIB CM','AfDB IRM']
matrix=np.array([[sum(r['policy']==p and r['iam']==m for r in rows) for m in iams] for p in policies])
fig,ax=plt.subplots(figsize=(7.0,4.0))
im=ax.imshow(matrix,cmap='Blues',vmin=0,vmax=45,aspect='auto')
ax.set_xticks(range(len(iams)),iams,rotation=25,ha='right');ax.set_yticks(range(len(policies)),policies)
for i in range(len(policies)):
    for j in range(len(iams)):
        ax.text(j,i,str(matrix[i,j]),ha='center',va='center',color='white' if matrix[i,j]>24 else '#1b2833')
ax.set_xlabel('AIIB-designated independent accountability mechanism')
ax.set_ylabel('Published applicable policy label')
fig.colorbar(im,ax=ax,label='Register entries',fraction=.025,pad=.03)
fig.tight_layout();save(fig,'policy_forum')

fig,ax=plt.subplots(figsize=(7.0,3.0))
countries=['Uzbekistan','Kazakhstan','Tajikistan','Mongolia','Kyrgyz Republic','Turkmenistan']
left=np.zeros(len(countries))
for iam in COLORS:
    values=np.array([sum(r['member']==c and r['iam']==iam for r in rows) for c in countries])
    ax.barh(countries,values,left=left,label=iam,color=COLORS[iam],height=.62)
    for i,v in enumerate(values):
        if v:ax.text(left[i]+v/2,i,str(v),ha='center',va='center',color='white' if iam=='AIIB PPM' else '#172329')
    left+=values
ax.invert_yaxis();ax.set_xlim(0,11);ax.set_xticks(range(0,11,2));ax.set_xlabel('Entries in end-2025 cofinancing register')
ax.text(.05,5,'No entries in this register',va='center',fontsize=8,color='#555555')
ax.legend(loc='upper center',bbox_to_anchor=(.5,-.25),ncol=4,frameon=False)
fig.tight_layout();save(fig,'regional_routes')

events=json.loads((ROOT/'data/shokpar_events.json').read_text())
selected=[e for e in events if e['id'] in {'intake','referral','suspension','registration','problem_solving','reports','withdrawal','cutoff'}]
labels=['AIIB intake','Referral to IPAM','Registration suspended','IPAM registration','Problem solving began','Four reports / unequal access','Problem solving discontinued','Open: compliance assessment']
fig,ax=plt.subplots(figsize=(7.0,3.7))
for i,e in enumerate(selected):
    low=mdates.date2num(date.fromisoformat(e['date_low']));hi=mdates.date2num(date.fromisoformat(e['date_high']))
    ax.plot([low,hi],[i,i],lw=6,color='#1b5a70',solid_capstyle='round')
    ax.scatter([(low+hi)/2],[i],s=20,color='#1b5a70')
    display=e['date_low'] if low==hi else e['date_low'][:7]+' (month only)'
    ax.annotate(display,((low+hi)/2,i),xytext=(8,-3),textcoords='offset points',fontsize=7.4)
ax.set_yticks(range(len(labels)),labels);ax.invert_yaxis()
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6));ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(date(2024,4,1),date(2027,6,1));ax.grid(axis='x',alpha=.18)
ax.set_xlabel('Documented event date; bars preserve month-level uncertainty')
fig.tight_layout();save(fig,'shokpar_timeline')

fig,ax=plt.subplots(figsize=(7,2.3));ax.axis('off');ax.set_xlim(0,1);ax.set_ylim(0,1)
text=[('Applicable\nnorms','Which policy\nand version?'),('Review\nmandate','Whose conduct\nis reviewed?'),('Evidentiary\nparticipation','Who can inspect\nthe reports?'),('Outcome','Agreement, finding\nor remedy?')]
for i,(title,sub) in enumerate(text):
    x=.005+i*.25
    box=FancyBboxPatch((x,.23),.225,.65,boxstyle='round,pad=0.007',facecolor='#edf2f4',edgecolor='#6a8794',linewidth=.8)
    ax.add_patch(box);ax.text(x+.1125,.69,title,ha='center',va='center',fontsize=8,fontweight='bold')
    ax.text(x+.1125,.40,sub,ha='center',va='center',fontsize=7.5)
    if i<3:ax.annotate('',xy=(x+.247,.55),xytext=(x+.229,.55),arrowprops={'arrowstyle':'->','color':'#555555'})
ax.text(.5,.055,'Separate questions; a documented answer to one does not establish the next.',ha='center',fontsize=8)
save(fig,'accountability_layers')
