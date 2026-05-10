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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    sr = (observation.get("self_role") or "").lower()
    orole = (observation.get("opponent_role") or "").lower()
    self_is_pursuer = ("purs" in sr) or ("purs" in orole and "evad" not in sr)
    self_is_evader = ("evad" in sr) or ("evad" in orole and "purs" not in sr)
    if not (self_is_pursuer or self_is_evader):
        self_is_pursuer = True

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_key = None

    curd = man(sx, sy, ox, oy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dist = man(nx, ny, ox, oy)

        if self_is_pursuer:
            # Minimize distance; deterministic tie-break preferring progress over staying.
            key = (dist, -abs(dx) - abs(dy), 0 if (nx == sx and ny == sy) else 1)
        else:
            # Maximize distance; tie-break toward actions that improve from current.
            delta = dist - curd
            key = (-dist, 0 if delta >= 0 else 1, -(delta), -abs(dx) - abs(dy), 0 if (nx == sx and ny == sy) else 1)

        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best