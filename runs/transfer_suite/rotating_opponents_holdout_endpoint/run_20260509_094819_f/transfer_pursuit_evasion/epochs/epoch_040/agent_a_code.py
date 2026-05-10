def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist(a, b):
        ax, ay = a
        bx, by = b
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("purs" in self_role) or (self_role == "captor") or (self_role == "pursuer")
    evader = not pursuer

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    center = ((w - 1) / 2.0, (h - 1) / 2.0)

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist((nx, ny), (ox, oy))
        cx, cy = center
        cd = abs(nx - cx) + abs(ny - cy)  # keep away from corner when evading; keep toward center when pursuing

        # Score higher is better
        if pursuer:
            score = (-d, -cd)
        else:
            score = (d, -cd)  # maximize distance, also prefer staying closer to center

        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]