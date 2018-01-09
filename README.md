# Why this repo?

Checkout [About This Site](https://tianjun.me/essays/54).

# Potential Risks

1. HTTPS
  每3个月需要renew一次，虽然添加了自动化脚本，仍需要确认下

1. File Sync
  目前采用Dropbox进行static目录的同步，该进程有挂掉的风险，本地static目录修改需谨慎，会影响线上所有静态文件

1. Cache
  Tag Counts 每次实时计算出来的，量大了以后显然很蠢（然而量并不大）

1. File_Watcher
  同步目录的时候，避免引入异常目录（否则会触发不可预知的增加和删除）

1. Git-Auto-Deploy
  该进程有挂掉的风险，需检查，由于采用的pull，git出现回滚等情况时，需手动解决
