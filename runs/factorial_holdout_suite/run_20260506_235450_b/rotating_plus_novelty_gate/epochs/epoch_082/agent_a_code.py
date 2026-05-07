def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    rs = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and valid(x, y):
                rs.append((x, y))
    if not rs:
        return [0, 0]

    best = (0, 0, -10**18)  # tx,ty,score
    for tx, ty in rs:
        sd = manh(sx, sy, tx, ty)
        od = manh(ox, oy, tx, ty)
        # Prefer resources we can reach sooner; if tie, prefer corner-leaning by x+y; and deny opponent.
        score = (od - sd) * 4 - sd + (tx + ty) * 0.01
        if score > best[2]:
            best = (tx, ty, score)

    tx, ty, _ = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Choose among valid moves the one that best reduces distance to target; break ties by opponent distance (deny them).
    best_mv = (0, 0)
    best_md = 10**9
    best_den = -10**18
    for mx, my in deltas:
        nx, ny = sx + mx, sy + my
        if not valid(nx, ny):
            continue
        md = manh(nx, ny, tx, ty)
        den = manh(nx, ny, tx, ty) - manh(ox, oy, tx, ty)  # lower means we are closer than opponent
        if md < best_md or (md == best_md and den > best_den):
            best_md = md
            best_den = den
            best_mv = (mx, my)

    return [int(best_mv[0]), int(best_mv[1])]