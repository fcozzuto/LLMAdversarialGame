def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def clamp_inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not resources:
        # deterministic fallback: drift toward center while respecting obstacles
        cx, cy = w // 2, h // 2
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not clamp_inside(nx, ny): 
                continue
            v = -(cheb(nx, ny, cx, cy))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # pick resource where we can beat opponent earliest; also prefer closer to center for tie-break stability
    cx, cy = w // 2, h // 2
    best_r = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # primary: smallest (ds - do); secondary: smaller ds; tertiary: prefer center; plus mild anti-blocking
        key = (ds - do, ds, cheb(rx, ry, cx, cy))
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    # choose one move that maximizes expected advantage for that target and avoids enabling opponent capture next step
    step_dir_x = 0 if rx == sx else (1 if rx > sx else -1)
    step_dir_y = 0 if ry == sy else (1 if ry > sy else -1)

    opp_step_x = 0 if rx == ox else (1 if rx > ox else -1)
    opp_step_y = 0 if ry == oy else (1 if ry > oy else -1)
    opp_next = (ox + opp_step_x, oy + opp_step_y)
    opp_can_reach_target_next = (opp_next[0] == rx and opp_next[1] == ry) and (0 <= opp_next[0] < w and 0 <= opp_next[1] < h) and opp_next not in obstacles

    best = [0, 0]
    bestv = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_inside(nx, ny):
            continue
        ns = cheb(nx, ny, rx, ry)
        no = cheb(ox, oy, rx, ry)  # opponent distance unchanged this turn
        advantage = (no - ns)  # higher is better
        # prefer moving toward target; discourage moving away or stalling
        progress = -cheb(nx, ny, rx, ry) + (0.25 * (dx == step_dir_x) + 0.25 * (dy == step_dir_y))
        # small penalty if we allow opponent immediate capture after our move (tie-break)
        block_penalty = 2.0 if opp_can_reach_target_next and (nx == rx and ny == ry) is False else 0.0
        # also avoid getting close to center only if still losing; keep deterministic but not aimless
        center_bias = -0.01 * cheb(nx, ny, cx, cy)
        v = 10.0 * advantage + progress + center_bias - block_penalty
        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best