def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_value(px, py):
        best = None
        best_val = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            tx, ty = r[0], r[1]
            if not (isinstance(tx, int) and isinstance(ty, int)):
                continue
            if not in_bounds(tx, ty) or (tx, ty) in blocked:
                continue
            myd = manh(px, py, tx, ty)
            opd = manh(ox, oy, tx, ty)
            # Prefer winning sooner; if tie, prefer closer to self (likely earlier pickup/safer).
            val = (opd - myd, -myd)
            if best_val is None or val > best_val:
                best_val = val
                best = (tx, ty)
        return best_val if best_val is not None else (-10**9, 0)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_delta = (0, 0)
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocked:
            continue
        val = best_value(nx, ny)
        # Small bias toward staying aligned with a target by favoring reduced distance to the current best target direction
        if best is None or val > best:
            best = val
            best_delta = (dx, dy)
    if best is None:
        return [0, 0]
    return [best_delta[0], best_delta[1]]