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

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                targets.append((x, y))
    if not targets:
        return [0, 0]

    best = None
    best_key = None
    for tx, ty in targets:
        myd = manh(sx, sy, tx, ty)
        opd = manh(ox, oy, tx, ty)
        # Prefer targets we can reach sooner; break ties by higher "margin"
        key = (opd - myd, -myd, tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    best_move = [0, 0]
    best_score = None
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        score = (manh(ox, oy, tx, ty) - manh(nx, ny, tx, ty), -manh(nx, ny, tx, ty))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move