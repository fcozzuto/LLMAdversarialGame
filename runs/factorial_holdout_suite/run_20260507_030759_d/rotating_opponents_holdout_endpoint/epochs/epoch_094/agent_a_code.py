def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Choose target: prefer resources where we are not farther than opponent, then closest, then deterministic tiebreak
    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = r[0], r[1]
        if not (isinstance(tx, int) and isinstance(ty, int)):
            continue
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        prefer = 0 if ds <= do else 1
        key = (prefer, ds, do, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    # Greedy step toward target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    cand = (sx + dx, sy + dy)
    if ok(cand[0], cand[1]):
        return [dx, dy]

    # Fallback: among valid moves, pick one that minimizes distance to target (then deterministic tiebreak)
    best_m = [0, 0]
    best_md = None
    best_det = None
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        det = (d, mdx, mdy)
        if best_md is None or det < (best_md, best_det[0], best_det[1]):
            best_md = d
            best_det = (mdx, mdy)
            best_m = [mdx, mdy]
    return best_m