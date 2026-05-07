def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for r in resources:
        if not isinstance(r, (list, tuple)) or len(r) < 2:
            continue
        tx, ty = r[0], r[1]
        if not inb(tx, ty) or (tx, ty) in obs:
            continue
        sd = md(sx, sy, tx, ty)
        od = md(ox, oy, tx, ty)
        adv = od - sd
        key = (adv, -sd)  # prioritize arriving first; tie-break closer
        if best_key is None or key > best_key:
            best_key, best = key, (tx, ty)

    if best is None:
        return [0, 0]
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_s = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        self_d = md(nx, ny, tx, ty)
        opp_d = md(ox, oy, tx, ty)
        # Try to increase our advantage and reduce distance; small bias away from opponent
        s = (opp_d - self_d) * 10 - self_d + (md(nx, ny, ox, oy) // 3)
        if best_s is None or s > best_s:
            best_s, best_m = s, (dx, dy)

    return [int(best_m[0]), int(best_m[1])]