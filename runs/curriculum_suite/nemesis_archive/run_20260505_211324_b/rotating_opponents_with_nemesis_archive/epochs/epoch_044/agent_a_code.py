def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y):
                obs.add((x, y))
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]
    def md(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)
    # Pick a target that is close to us and far from the opponent
    tx, ty = min(res, key=lambda p: (md(sx, sy, p[0], p[1]), -md(ox, oy, p[0], p[1]), p[0], p[1]))
    best = (10**9, -10**9, 0, 0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                pass
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d1 = md(nx, ny, tx, ty)
            d2 = md(nx, ny, ox, oy)
            # primary: reduce distance to target; secondary: increase distance from opponent
            key = (d1, -d2, abs(dx) + abs(dy), dx, dy)
            if key < (best[0], -best[1], best[2], best[3], best[0]):
                best = (d1, d2, abs(dx) + abs(dy), dx if dx or dy else 0)
                chosen = [dx, dy]
    try:
        return chosen
    except NameError:
        return [0, 0]