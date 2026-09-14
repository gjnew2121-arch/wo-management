// STATUS — single source of truth
export const STATUS = {
  OPEN:   { key:'OPEN',   label:'Open WO',                       dot:'#9e9e9e', rowClass:'row-open'   },
  CLOSED: { key:'CLOSED', label:'WO Completed',                  dot:'#4caf50', rowClass:'row-closed' },
  DOCS:   { key:'DOCS',   label:'WO Completed – Docs in office', dot:'#2196f3', rowClass:'row-docs'   },
  CNX:    { key:'CNX',    label:'Cancelled',                     dot:'#f44336', rowClass:'row-cnx'    },
}

export function getDisplayStatus(wo) {
  if (wo.status === 'CNX')                              return STATUS.CNX
  if (wo.status === 'CLOSED' && wo.wp_filed === 'YES') return STATUS.DOCS
  if (wo.status === 'CLOSED')                           return STATUS.CLOSED
  return STATUS.OPEN
}
