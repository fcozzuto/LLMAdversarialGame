def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obs = observation.get("obstacles", []) or []
    blocked = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    unclaimed = observation.get("unclaimed_cells") or []
    U = [(int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2]

    self_terr = observation.get("self_territory") or []
    self_set = set((int(p[0]), int(p[1])) for p in self_terr if isinstance(p, (list, tuple)) and len(p) >= 2)

    opp_terr = observation.get("opponent_territory") or []
    opp_set = set((int(p[0]), int(p[1])) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2)

    target = None
    if U:
        tx, ty = min(U, key=lambda t: (man(sx, sy, t[0], t[1]), t[0], t[1]))
        target = (tx, ty)
    elif opp_set:
        candidates = set()
        for x, y in self_set:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in opp_set:
                        candidates.add((nx, ny))
        if candidates:
            tx, ty = min(candidates, key=lambda t: (man(sx, sy, t[0], t[1]), t[0], t[1]))
            target = (tx, ty)
        else:
            tx, ty = ox, oy
            target = (tx, ty)
    else:
        target = (ox, oy)

    best = None
    best_score = None
    tx, ty = target

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        score = 0
        if (nx, ny) == (tx, ty):
            score -= 100000
        score += man(nx, ny, tx, ty)
        if (nx, ny) in self_set:
            score += 1
        if opp_set and (nx, ny) in opp_set:
            score -= 50
        if best is None or score < best_score or (score == best_score and (dx, dy) < best):
            best = (dx, dy)
            best_score = score

    return [best[0], best[1]] if best is not None else [0, 0]