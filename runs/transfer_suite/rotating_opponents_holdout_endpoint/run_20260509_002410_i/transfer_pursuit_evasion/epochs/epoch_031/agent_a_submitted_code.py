def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx + dy

    sr = (observation.get("self_role") or "").lower()
    self_is_pursuer = ("purs" in sr) and ("evad" not in sr)
    if not ("purs" in sr or "evad" in sr):
        self_is_pursuer = True

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bestv = None

    targets = res if res else [(ox, oy)]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        here = (nx, ny)
        if res:
            d = min(manh(here, r) for r in targets)
            v = d if self_is_pursuer else -d
        else:
            d = man(here, (ox, oy))
            v = d if not self_is_pursuer else -d
        key = (v, dx, dy)
        if best is None or (key < bestv):
            best = (dx, dy)
            bestv = key

    if best is None:
        return [0, 0]
    return [best[0], best[1]]