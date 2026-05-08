def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    op = observation.get("opponent_position") or sp
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set()
    for c in observation.get("unclaimed_cells") or []:
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    self_t = set()
    for c in observation.get("self_territory") or []:
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                self_t.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (None, -10**9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dopp = abs(nx - ox) + abs(ny - oy)
        bonus = 30 if (nx, ny) in unclaimed else 0
        own = 6 if (nx, ny) in self_t else 0
        score = dipp = dott = 0  # avoid accidental NameError
        score = bonus + own + doppel = 0
        # deterministic score calculation
        score = bonus + own + (dopp * 2) - (abs(nx - sx) + abs(ny - sy))
        if score > best[1] or (score == best[1] and (dx, dy) == (0, 0)):
            best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]