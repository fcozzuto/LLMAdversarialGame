def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def neigh_moves(x, y):
        best = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    best.append((dx, dy, nx, ny))
        return best or [(0, 0, x, y)]

    cand_moves = neigh_moves(sx, sy)

    # Evaluate each possible neighbor by the best resource it could reach soonest.
    def best_target_score(px, py):
        self_dmin = 10**9
        opp_dmin = 10**9
        # Prefer resources where we can arrive first; if tied/behind, minimize the gap.
        for rx, ry in resources:
            sd = abs(rx - px) + abs(ry - py)
            od = abs(rx - ox) + abs(ry - oy)
            gap = od - sd  # positive if we are closer
            # Tie-break: earlier arrival is better; also slightly favor resources nearer to opponent
            # to reduce their chances if we are behind.
            if gap > self_dmin:
                pass
            if gap > 0:
                sc = 1000 + gap * 10 - sd
            else:
                sc = gap * 20 - sd
            # incorporate density-like deterministic preference: nearer to center
            center_bias = -0.01 * (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2))
            if sc + center_bias > self_dmin:
                self_dmin = sc + center_bias
                opp_dmin = od
        return self_dmin, opp_dmin

    best = None
    best_val = -10**18
    for dx, dy, nx, ny in cand_moves:
        val, _ = best_target_score(nx, ny)
        # Small deterministic preference for progressing (avoid oscillation when equal)
        progress = -(abs(nx - sx) + abs(ny - sy))
        val2 = val + progress
        if val2 > best_val:
            best_val = val2
            best = [dx, dy]

    return best if best is not None else [0, 0]