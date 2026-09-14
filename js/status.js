// STATUS — single source of truth
export const STATUS = {
  OPEN:   { key:'OPEN',   label:'Open WO',                       dot:'#9e9e9e', rowBg:'#ffffff',                   rowBorder:'#e0e0e0' },
  CLOSED: { key:'CLOSED', label:'WO Completed',                  dot:'#2e7d32', rowBg:'rgba(76,175,80,0.25)',      rowBorder:'#4caf50' },
  DOCS:   { key:'DOCS',   label:'WO Completed – Docs in office', dot:'#1565c0', rowBg:'rgba(33,150,243,0.25)',     rowBorder:'#2196f3' },
  CNX:    { key:'CNX',    label:'Cancelled',                     dot:'#c62828', rowBg:'rgba(244,67,54,0.22)',      rowBorder:'#f44336' },
}

export function getDisplayStatus(wo) {
  if (wo.status === 'CNX')                              return STATUS.CNX
  if (wo.status === 'CLOSED' && wo.wp_filed === 'YES') return STATUS.DOCS
  if (wo.status === 'CLOSED')                           return STATUS.CLOSED
  return STATUS.OPEN
}
