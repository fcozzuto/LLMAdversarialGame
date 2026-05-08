def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    dirs_tiebreak = {(0, 0): 0, (1, 0): 1, (0, 1): 2, (-1, 0): 3, (0, -1): 4, (1, 1): 5, (1, -1): 6, (-1, 1): 7, (-1, -1): 8}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Strategic target: prefer cells unclaimed far from opponent; else expand into opponent territory
    candidates = list(unclaimed) if unclaimed else list(oppT)
    target = None
    if candidates:
        candidates.sort(key=lambda t: (man(sx, sy, t[0], t[1]), -man(ox, oy, t[0], t[1]), min(t[0], t[1], w - 1 - t[0], h - 1 - t[1]), t[0], t[1]))
        target = candidates[0]

    best = (None, -10**9, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        pr = 0
        if cell in unclaimed:
            pr += 1000
        if cell in oppT:
            pr += 400
        if cell in selfT:
            pr += 100
        if target is not None:
            pr -= man(nx, ny, target[0], target[1]) * 3
        pr -= man(nx, ny, ox, oy) * 0.1  # drift away slightly
        # If hitting opponent territory early is dangerous, prefer distance; but still capture if it's the only good move.
        pr -= 2 if (dx, dy) == (0, 0) and target is not None else 0
        tieb = dirs_tiebreak[(dx, dy)]
        if pr > best[1] or (pr == best[1] and tieb < best[2]):
            best = (cell, pr, tieb)

    # If all moves invalid, stay
    if best[0] is None:
        return [0, 0]
    nx, ny = best[0]
    return [nx - sx, ny - sy]