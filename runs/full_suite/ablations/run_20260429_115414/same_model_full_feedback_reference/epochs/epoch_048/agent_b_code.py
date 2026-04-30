def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            v = -cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Deterministic evaluation: prefer moves that can secure some resource sooner than opponent.
    opp_time_pref = 0
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Baseline: keep moving toward nearest resource.
        our_best = 10**9
        gain_best = -10**9
        our2_best = 10**9
        for rx, ry in resources:
            our_t = cheb(nx, ny, rx, ry)
            opp_t = cheb(ox, oy, rx, ry)
            if our_t < our_best:
                our_best = our_t
            # If we can be at the resource no later than opponent, that's strong.
            gain = opp_t - our_t
            if gain > gain_best:
                gain_best = gain
                our2_best = our_t

        # Tie-break: discourage positions that let opponent get very close while we stall.
        opp_close = cheb(nx, ny, ox, oy)
        val = 20 * gain_best - 3 * our_best - 0.5 * opp_close
        # Mild preference to avoid staying still if equal.
        if dx == 0 and dy == 0:
            val -= 0.2

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]