# Vision is the bottleneck: seven action-chunking tricks for a VLA, re-measured on a Jetson Orin NX

*Ravindu Somawansa, Shisso Robotics. Draft, 4-page workshop version. Rendered by `make_paper.py` from the result
files: every number below is a placeholder filled from `numbers.json`, which records each value's anchor. Nothing new
was run.*

## Abstract

We re-measured seven training-free methods for action chunking in flow-matching VLAs. Their papers report numbers from
desktop GPUs. We ran them where a low-cost robot runs its policy, with SmolVLA on a Jetson Orin NX. All tests share
one checkpoint and the same recorded episodes. Each test had its threshold committed before the run, and every number
traces to a result file and a protocol commit. On this board the vision encoder takes {{glat_vision}} of
{{glat_total}} ms of server time per chunk (25 W). The two methods that act on the seam between chunks pass. A
gradient-free prefix overwrite cuts the boundary jump by {{ow_cut_20}} % or more. Movement-primitive seam conditioning
removes most of the seam jerk. The sampling methods do not transfer. vla.cpp samples in sequence, so every N-sample
method pays for N chunks one after another.

## 1 Introduction

Multiple training-free chunking tricks for flow-matching VLAs have come out this year. Their numbers always come from
strong desktop or data-centre GPUs (RTX 4090, A100, H100, RTX 5090). On these, a chunk costs barely tens of
milliseconds and spare compute is plentiful. A robot people can buy runs its policy on an edge GPU. There most of the
chunk goes to the vision encoder, which these tricks don't affect. We measured how much of each trick is left on such
a board.

Our robot is an SO-101 arm [arXiv:2606.08881] with a Jetson Orin NX 16 GB. It runs SmolVLA [arXiv:2506.01844] through
vla.cpp, a C++ inference engine, on episodes recorded with LeRobot. This paper started once SmolVLA ran on the arm
through vla.cpp. We then looked at where the rest of a chunk's time went, and at which published tricks could still
help. We took seven of them. Each one is a gate with a bar committed before the number. Offline effects get an episode
bootstrap, and latencies are medians of at least 50 calls. The appendix maps every number to its result file and
protocol commit.

## 2 Where the time goes

We follow one chunk of ten Euler steps at full power (MAXN_SUPER). It costs {{n10_ms}} ms end to end (Fig. 1). Vision
takes {{vision_ms_a2}} ms and prefill {{prefill_ms}} ms. Each denoise step takes {{step_ms}} ms. At 25 W the
server-side split is {{glat_vision}} ms of vision in {{glat_total}} ms. A trick that only touches the denoising loop
works on at most a quarter of the chunk.

Two power modes appear in this paper. Each gate's protocol froze the mode it ran in. The serving split and the
boundary experiments ran at 25 W, and the latency experiments at full power. Every number below carries its mode.

![Fig. 1 — where one SmolVLA chunk's time goes on the Orin NX (vla.cpp, ten Euler steps, MAXN_SUPER): vision is most of it](fig/latency_split.png)

## 3 Seven tricks, one checkpoint

All offline effects use the same SmolVLA checkpoint and the same 20 recorded episodes, with 254 chunk boundaries per
delay. Table 1 gives every effect, bar and verdict.

Two tricks act on the seam between chunks, and both pass. The first overwrites the new chunk's executed prefix with
the actions already committed. It passes the 50 % jump-cut bar at every delay, in PyTorch and in vla.cpp. In vla.cpp
it adds {{cpp_ow_added_ms}} ms per chunk. The second is movement-primitive chunking [arXiv:2610.39451]. Projecting
each chunk onto ten Gaussian bases keeps the error within its bar and removes within-chunk jerk. Conditioning on the
last action sent removes {{sm_seam25}}–{{sm_seam50}} % of the seam jerk at {{sm_cost}}° of error. Its paper reports
{{sm_paper}} %. We measured on the commanded stream only.

Exact real-time chunking [arXiv:2506.07339] inpaints the prefix with guidance instead of overwriting it. It cuts the
jump by less than 50 % at every delay (Fig. 2). In PyTorch it costs {{exact_over_naive}}× a naive chunk.

Cutting the Euler steps from ten to two [arXiv:2610.32102] saves {{n2_saved_ms}} ms per chunk at full power. The
vision cost is much larger. The paper claims that the action cloud contracts around an unchanged centroid. It reports
a cloud ratio of {{r2_paper}} on π0. Our ratio is {{r2_ratio}}. It falls between the bar of {{r2_bar}} and the fail
line of {{r2_failline}}, so the claim is {{r2_verdict}} here. The paper also expects fewer steps to remove edge-GPU
thermal throttling. Our Orin did not throttle at ten steps in either power mode. We keep ten steps, as the protocol
says while the contraction is unproven.

Two tricks sample several chunks per decision. Speculative chunk selection [arXiv:2610.28019] samples four candidates.
It uses the pre-commit frame to pick the one closest to the recorded teleoperation continuation. Offline it beats a
random pick (one continuation per frame, training-set episodes, open loop). Its paper promises no added control-step
delay. On the Orin, vla.cpp samples the candidates in sequence. A cycle costs {{pact_ms}} ms and {{pact_d}} control
ticks, against {{naive_d}} for a naive chunk (Fig. 3). Entropy-adaptive chunk length [arXiv:2604.04161] samples 20
chunks per decision. One decision takes {{aac_n20_ms}} ms on the Orin. The threshold was {{aac_bar_ms}} ms. The chosen
length also sits at the floor in both task phases. The jump is no better than with fixed chunks and the overwrite.

Table 1: Seven tricks on one checkpoint: what each acts on, its offline effect, the pre-registered bar, the verdict and its cost on the Orin NX.

| trick | acts on | offline effect | bar | verdict | cost on the Orin | mode |
|---|---|---|---|---|---|---|
| prefix overwrite | seam | jump −{{cpp_cut_8}} / −{{cpp_cut_12}} / −{{cpp_cut_20}} % (vla.cpp, d = 8/12/20); PyTorch −{{ow_cut_8}} / −{{ow_cut_12}} / −{{ow_cut_20}} % | cut ≥ 50 % | pass | +{{cpp_ow_added_ms}} ms per chunk | 25 W |
| exact RTC guidance | seam | jump −{{ex_cut_8}} / −{{ex_cut_12}} / −{{ex_cut_20}} % | cut ≥ 50 % | fail | {{pt_exact_ms}} vs {{pt_naive_ms}} ms naive ({{exact_over_naive}}×, PyTorch) | 25 W |
| MP projection | within-chunk jerk | error {{sm_err}}°, jerk −{{sm_jerk}} % | error ≤ +0.30° | pass | < 1 ms | — |
| seam conditioning | seam jerk | −{{sm_seam25}} % (overlap 25) / −{{sm_seam50}} % (sync) at {{sm_cost}}° | seam jerk ≤ 0.40× | pass | < 1 ms | — |
| two Euler steps | denoise loop | cloud ratio {{r2_ratio}} (CI {{r2_lo}}–{{r2_hi}}) | ≤ 0.70 | {{r2_verdict}} | {{n2_ms}} vs {{n10_ms}} ms per chunk | MAXN_SUPER |
| speculative selection (PACT) | chunk choice | {{pact_sel}}° vs a random pick (CI {{pact_sel_lo}} to {{pact_sel_hi}}) | CI < 0, no added delay | selection pass, delay fail | {{pact_ms}} ms per cycle, {{pact_d}} ticks vs {{naive_d}} | MAXN_SUPER |
| adaptive length (AAC) | chunk length | h* {{aac_h_transport}} / {{aac_h_grasp}} (transport / grasp); jump {{aac_jump}} vs {{aac_fixed_jump}} | transport ≥ grasp + 2; N = 20 ≤ {{aac_bar_ms}} ms | fail | {{aac_n20_ms}} ms per decision | MAXN_SUPER |

![Fig. 2 — median boundary-jump cut against naive asynchronous execution (254 boundaries per delay, 25 W): the overwrite clears the 50 % bar at every delay, exact RTC guidance does not.](fig/jump_cut.png)

![Fig. 3 — cost per decision on the Orin NX (log scale, MAXN_SUPER): both sampling methods miss their bar (dashed: AAC's {{aac_bar_ms}} ms; PACT's bar is one chunk, {{pact_tgen1}} ms).](fig/decision_cost.png)

## 4 What transfers to the board

The prefix overwrite and the primitive projection with seam conditioning act on the seam. Each costs under a
millisecond on this board. We keep ten Euler steps until the contraction passes its threshold. The two-step saving is
small next to vision. Exact guidance, speculative selection and adaptive length all pay for N chunks in series on a
sequential engine. If you run one of them on an edge board, check first whether your engine samples in a batch,
because ours does not. This version is offline and latency only. The closed-loop columns on the arm, for seam
smoothing and for the overwrite in the robot client, belong to a longer version.

## 5 Related work

Other chunking tricks are also reported on desktop-class GPUs. We did not re-measure them here. One extends the
executing chunk instead of resampling [arXiv:2610.05719]. One drives reactive chunking with a latent world model
[arXiv:2606.18589]. One fine-tunes the policy for latency with reinforcement learning [arXiv:2608.23831]. On the
engine side, TurboVLA [arXiv:2607.27205] pushes VLA throughput on a desktop GPU. vla.cpp, the engine we measure, runs
VLAs on edge boards. Two works use the same arm to evaluate policies. A standardized benchmark reports failures and
recoveries of VLA policies [arXiv:2606.08881]. A fleet of SO-101 cells evaluates policies at scale [arXiv:2607.24481].
We re-measure the execution tricks around one policy, under bars fixed before the run.

## 6 Limitations

The sampling result depends on the engine. vla.cpp samples sequentially. We contribute to vla.cpp, and the overwrite
runs on our fork (`ravediamond/vla.cpp`). Parity and determinism checks against PyTorch on the same board are in the
gate logs. A batched sampler would test the sampling result, and we have not run one. Effects other than latency are
offline. They come from 20 recorded demonstrations of one task family (bowls), and the policy was trained on them. The
arm gates for seam smoothing and for the overwrite in the robot client have not run. We left out the adaptive-length
arm gate because SmolVLA is at ceiling on this task, so a gain could not show. Latency rows run at MAXN_SUPER, and the
serving and boundary rows at 25 W. Power mode is a confound wherever the two are compared. The study covers one
policy, SmolVLA at 450M. π0-class models do not fit on the Orin.

## Appendix: from plain name to gate

Every number in this paper is recomputable from the repository; this table maps each experiment to its files.

| experiment | repro folder | expected files | protocol commit | bar |
|---|---|---|---|---|
| serving split (25 W) | repro/glat2 | glat2_gpu640_summary.json | {{bar_glat}} | overhead ≤ 100 ms, ≤ 2 % over the 238 ms baseline |
| latency split, two Euler steps | repro/horizon-depth | a2_latency.json, a1_cloud.json | {{bar_hd}} | cloud ratio ≤ 0.70; N = 2 ≤ 0.85 × N = 10 |
| chunk boundary (overwrite, exact) | repro/chunk-boundary | g13b_summary.json, g13b_preflight.json, vlacpp_overwrite_summary.json | pre-registered 2026-10-19 (see the folder's README) | best gradient-free cut ≥ 50 %, drift ≤ +10 %, within 667 ms |
| MP projection, seam conditioning | repro/smooth-chunking | a_summary.json | {{bar_sm}} | error ≤ +0.30°; seam jerk ≤ 0.40× |
| speculative selection | repro/pact | gate_a.json, gate_b.json | {{bar_pact}} | ticks ≤ naive; beats a random pick (CI < 0) |
| adaptive length | repro/aac | gate0.json, gate1_latency.json | {{bar_aac}} | transport h* ≥ grasp + 2; N = 20 ≤ 298 ms |

## References

Real-time chunking — arXiv:2506.07339 · Smooth MP chunking — arXiv:2610.39451 · Horizon × depth — arXiv:2610.32102 ·
PACT-VLA — arXiv:2610.28019 · Adaptive action chunking — arXiv:2604.04161 · SmolVLA — arXiv:2506.01844 ·
TurboVLA — arXiv:2607.27205 · When to switch — arXiv:2610.05719 · DREAM-Chunk — arXiv:2606.18589 ·
Act while waiting — arXiv:2608.23831 · SO-101 VLA benchmark — arXiv:2606.08881 · ArmnetBench — arXiv:2607.24481 ·
vla.cpp — github.com/VinRobotics/vla.cpp · LeRobot — github.com/huggingface/lerobot ·
SO-ARM100/SO-101 — github.com/TheRobotStudio/SO-ARM100.
