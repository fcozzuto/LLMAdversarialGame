def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    blocked = obstacles

    target = None
    if unclaimed:
        target = min(unclaimed, key=lambda c: (man(c[0], c[1], ox, oy), c[0], c[1]))

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        if (nx, ny) in oppT:
            continue

        v = 0
        if (nx, ny) in unclaimed:
            v += 100000
        if target is not None:
            v += -man(nx, ny, target[0], target[1]) * 10
        else:
            v += -(man(nx, ny, w // 2, h // 2))
            v += -man(nx, ny, ox, oy) * 0.5

        # deterministic tie-break
        key = (-(v), dx, dy, nx, ny)
        if best is None or key < bestv:
            bestv = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]