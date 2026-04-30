def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    blocked = set(obstacles)
    blocked.discard((sx, sy))

    if not resources:
        # No visible resources: move to maximize distance from opponent (defensive)
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            val = cheb(nx, ny, ox, oy)
            if val > best[1]:
                best = ((dx, dy), val)
        return best[0] if best[0] is not None else [0, 0]

    # Pick a target resource where we are relatively closer than opponent
    best_r = None
    best_val = None  # smaller is better
    for rx, ry in resources:
        if (rx, ry) in blocked:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer (smaller ds-do). Slightly bias towards nearer resources.
        val = (ds - do, ds)
        if best_val is None or val < best_val:
            best_val = val
            best_r = (rx, ry)
    if best_r is None:
        # All resources blocked or none: defensive
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            val = cheb(nx, ny, ox, oy)
            if val > best[1]:
                best = ((dx, dy), val)
        return best[0] if best[0] is not None else [0, 0]

    rx, ry = best_r
    # Evaluate candidate next steps
    best_move = None
    best_score = None  # larger is better
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        dist_self = cheb(nx, ny, rx, ry)
        dist_opp = cheb(ox, oy, rx, ry)
        # Main objective: reduce our distance to target while denying opponent advantage.
        # Secondary: keep distance from opponent to reduce contest.
        contest = (dist_self - dist_opp)
        sep = cheb(nx, ny, ox, oy)
        # Collecting: if next is on resource, strongly favor.
        on_res = 1 if (nx, ny) in set(tuple(p) for p in resources) else 0
        score = (1000000 * on_res) - 1000 * contest - dist_self + 0.01 * sep
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return list(best_move) if best_move is not None else [0, 0]