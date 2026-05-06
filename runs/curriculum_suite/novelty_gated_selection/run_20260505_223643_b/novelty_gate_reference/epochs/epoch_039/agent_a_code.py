def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0] or 0), int(sp[1] or 0)
    ox, oy = int(op[0] or 0), int(op[1] or 0)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def mdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not res:
        return [0, 0]

    opp_w = 1.9

    # Pick a target resource that maximizes (opp_delay advantage), deterministic tie-break by coords.
    best = None
    best_key = None
    for x, y in res:
        ds = mdist(sx, sy, x, y)
        do = mdist(ox, oy, x, y)
        key = (ds - opp_w * do, x, y)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)
    tx, ty = best

    # Choose the best immediate move among 9 deltas by minimizing estimated disadvantage after moving.
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Deterministic preference: stay last among equal scores by ordering deltas with (0,0) near end.
    deltas.sort(key=lambda d: (d[0] == 0 and d[1] == 0, d[0], d[1]))

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        ns = mdist(nx, ny, tx, ty)
        no = mdist(ox, oy, tx, ty)
        # If we're on target, strongly prefer.
        on_target = 0 if (nx == tx and ny == ty) else 1
        # Small term encourages movement progress and reduces wandering.
        progress = mdist(sx, sy, tx, ty) - ns
        score = (ns - opp_w * no) + on_target * 0.0 - 0.15 * progress + 0.02 * (dx * dx + dy * dy)

        # Prefer moves with lower score; tie-break by deltas deterministically.
        key = (score, dx, dy)
        if best_score is None or key < (best_score, best_move[0], best_move[1]):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [dx, dy]