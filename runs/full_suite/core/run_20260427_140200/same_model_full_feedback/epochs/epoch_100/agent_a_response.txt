def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        # Deterministic contest: move to reduce distance to opponent
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
                continue
            v = (cheb(nx, ny, ox, oy), cheb(nx, ny, sx, sy))
            if best is None or v < best[0]:
                best = (v, [dx, dy])
        return best[1] if best else [0, 0]

    # Pick a target resource we can arrive at before opponent; otherwise the one that least favors them.
    best_res = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer ds < do strongly; else pick smallest ds, and most-negative (do - ds).
        diff = do - ds
        key = (diff < 0, -diff, ds, rx, ry)  # prefer diff>=0 first; then larger diff; then nearer
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res

    # Greedy one-step with obstacle avoidance and slight anti-contest (stay farther from opponent if tied).
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
            continue
        our_to_target = cheb(nx, ny, tx, ty)
        opp_to_target = cheb(ox, oy, tx, ty)  # constant for this move; keep deterministic tie-break
        our_to_opp = cheb(nx, ny, ox, oy)
        # Value: minimize our distance to target; maximize separation from opponent as secondary.
        val = (our_to_target, our_to_target - opp_to_target, -our_to_opp, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move