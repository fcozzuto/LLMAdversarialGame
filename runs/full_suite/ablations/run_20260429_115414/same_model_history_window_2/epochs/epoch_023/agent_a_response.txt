def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(x1, y1, x2, y2):
        ax = x1 - x2; ax = -ax if ax < 0 else ax
        ay = y1 - y2; ay = -ay if ay < 0 else ay
        return ax if ax > ay else ay

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Deterministic policy: try to secure resources where we can arrive no later than opponent,
    # otherwise improve "threat pressure" by moving into the most contested resource cluster.
    best = None
    best_val = -10**18
    idx_bias = observation.get("turn_index", 0) % (len(resources) + 1) if resources else 0

    for dx, dy, nx, ny in legal:
        obst_pen = 0
        for bx, by in blocked:
            d = cheb(nx, ny, bx, by)
            if d <= 1: obst_pen -= 6
            elif d == 2: obst_pen -= 2

        our_here = 0.0
        opp_here = 0.0
        cluster = 0
        adv_cnt = 0
        best_adv = -10**9

        for i, (rx, ry) in enumerate(resources):
            d1 = cheb(nx, ny, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            if d1 <= 4 or d2 <= 4:
                cluster += 1
            if d1 <= d2:
                adv_cnt += 1
                gain = 30 - 6 * d1 + 0.25 * ((len(resources) - i) if resources else 0)
                best_adv = gain if gain > best_adv else best_adv
            else:
                # contested/deny: moving closer when opponent is closer still matters
                opp_here += 0.15 * (d2 - d1)

            our_here += 0.02 * (d2 - d1)  # shift toward parity

        val = 0.0
        if resources:
            if adv_cnt > 0:
                val += 120 + 8 * adv_cnt + best_adv + 2.5 * cluster
            else:
                val += 20 + 1.5 * cluster + 4.0 * opp_here + 3.0 * our_here
        else:
            val += -cheb(nx, ny, ox, oy)  # default: drift away from opponent

        # Mild preference: keep moving toward the overall resource centroid
        if resources:
            cx = 0; cy = 0
            for rx, ry in resources:
                cx += rx; cy += ry
            cx //= len(resources); cy //= len(resources)
            val += 0.03 * (cheb(sx, sy, cx, cy) - cheb(nx, ny, cx, cy))

        # Tiny deterministic tie-break using index_bias and move ordering
        val += (idx_bias + (dx + 1) * 3 + (dy + 1)) * 1e-6
        val += obst_pen

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]