def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                obstacles.add((int(p[0]), int(p[1])))
            except:
                pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    target = None
    bestd = None

    for c in (observation.get("resources", []) or []):
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if inb(x, y) and (x, y) not in obstacles:
                d = man(sx, sy, x, y)
                if bestd is None or d < bestd:
                    bestd, target = d, (x, y)

    if target is None:
        for c in (observation.get("unclaimed_cells", []) or []):
            if isinstance(c, (list, tuple)) and len(c) >= 2:
                x, y = int(c[0]), int(c[1])
                if inb(x, y) and (x, y) not in obstacles:
                    d = man(sx, sy, x, y)
                    if bestd is None or d < bestd:
                        bestd, target = d, (x, y)

    if target is None:
        target = (ox, oy)

    tx, ty = target
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    bestscore = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = man(nx, ny, tx, ty)
        # Prefer getting closer to target; small tie-break to avoid approaching opponent too much.
        score = d * 10 + man(nx, ny, ox, oy)
        if bestscore is None or score < bestscore:
            bestscore, best = score, (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]