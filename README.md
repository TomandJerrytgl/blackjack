# Blackjack

Pygame Blackjack，已在 Python 3.11 和 Pygame 2.5.2 下测试。

## 安装和运行

```powershell
py -3.11 -m pip install -r requirements.txt
py -3.11 main.py
```

Start 后选择 New Game 或 Load Game。下注时左键点击筹码增加下注，
右键退回筹码，再点击 Deal。玩家可以 Hit、Stand，以及在规则和资金
允许时 Double 或 Split。

## 功能与规则

- 五副牌；局间剩余少于 104 张时重新创建并洗牌。
- Ace 按 1 或 11 计算，庄家 Soft 17 停牌。
- 普通胜利返还两倍下注，Natural Blackjack 返还 2.5 倍，Push 退还本金。
- 庄家明牌为 Ace 时提供半注 Insurance，盈利按 2:1 结算；Ace 或十点明牌检查 Blackjack。
- 起手两张且资金充足可 Double：再扣一份下注，仅抽一张并停牌。
- 相同 rank 可 Split 一次；两手分别操作和结算，Split A 每手仅补一张。
  Split 后的 21 不算 Natural Blackjack。
- 五个手动存档槽，局间保存，覆盖前确认。存档包含余额、牌堆顺序、
  公开牌历史与战绩，保存在本地 `saves/`，不上传 Git。
  下注界面保存前会退还未开局下注。
- 战绩按完成的整局计数，含保险的净收益大于零计为胜场；Split 仍算一局。

## Show Odds

后台分批 Monte Carlo，每项默认 12,000 个样本；固定种子和缓存使相同公开
状态的最终结果稳定。未知牌池包含庄家暗牌，计算不读取真实暗牌或牌堆顺序，
并考虑庄家检查后公开的“没有 Blackjack”信息。

Stand 为立即停牌；Hit 后不足 17 继续抽牌、达到 17 停牌；Double 只抽一张；
Split 后两手按相同策略模拟（Split A 除外）。后续不再 Double 或 Split。
Split 显示两手平均 Win/Push/Lose 概率，并非整局净盈利概率，也不代表最优策略。

## 测试

```powershell
py -3.11 -m unittest -v test_blackjack test_probability
```

测试使用无窗口 SDL 模式，涵盖规则、赔付、连续两局、存档、暗牌隔离和计算期间的事件响应。

## 模块

- `main.py`：窗口初始化、阶段调度与清理。
- `game_stage.py`：逐帧阶段、游戏规则、资金和战绩。
- `gui.py`：Pygame 绘制。
- `deck.py`：牌堆创建、洗牌、抽牌及牌面转换。
- `probability.py`：后台概率模拟与缓存。
- `save_manager.py`：五槽 JSON 存档及校验。

所有阶段接受 `(screen, clock, stage_info)`，通过修改 `stage_name` 切换，
每帧只读取一次事件。存档不支持恢复一局中途的操作。

当前 Pygame 版本的入口是 `main.py`。2024 年旧版文件已从当前分支移除，
仍可通过 Git 提交历史查看或恢复。
