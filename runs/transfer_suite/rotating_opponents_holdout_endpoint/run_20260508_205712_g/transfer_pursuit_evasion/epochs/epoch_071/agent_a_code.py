def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
        elif isinstance(r, dict):
            x = r.get("x", r.get("X", None))
            y = r.get("y", r.get("Y", None))
            if x is not None and y is not None:
                x, y = int(x), int(y)
                if 0 <= x < w and 0 <= y < h:
                    resources.append((x, y))

    sr = str(observation.get("self_role", "")).lower()
    self_is_pursuer = ("pursuer" in sr) or ("pred" in sr) or ("catch" in sr)
    if "evader" in sr:
        self_is_pursuer = False

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-(10**18), 0, 0)
    any_free = False

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        any_free = True

        do = man(nx, ny, ox, oy)
        if resources:
            dr = min(man(nx, ny, rx, ry) for rx, ry in resources)
        else:
            dr = 0

        if self_is_pursuer:
            score = (-dr) * 2 + (-do)
        else:
            score = (-do) * (-1) + (-dr) * 0.5  # maximize distance from opponent

        if score > best[0]:
            best = (score, dx, dy)

    if any_free:
        return [best[1], best[2]]

    # All moves blocked: stay deterministic, try in-bounds non-obstacle preference, else stay.
    if (sx, sy) not in obstacles:
        return [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            return [dx, dy]
    return [0, 0]