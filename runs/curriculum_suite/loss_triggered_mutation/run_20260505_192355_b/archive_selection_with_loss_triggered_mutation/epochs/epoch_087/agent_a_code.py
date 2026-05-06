def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst
    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    if not inb(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not res:
        for dx, dy in moves:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    # Choose best target for which we have/seek advantage over opponent.
    best = None
    for tx, ty in res:
        sd = dist((sx, sy), (tx, ty))
        od = dist((ox, oy), (tx, ty))
        key = (sd - od, sd)  # smaller is better; we prefer resources opponent can't reach first
        if best is None or key < best[0]:
            best = (key, (tx, ty))
    tx, ty = best[1]

    # One-step lookahead: pick legal move maximizing advantage toward target, with small denier pressure.
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nsd = dist((nx, ny), (tx, ty))
        nod = dist((ox, oy), (tx, ty))
        # Prefer getting closer; also slightly prefer moves that increase opponent-target disadvantage.
        # Add slight bonus for reducing our overall distance to some (any) resource we can still contest.
        any_bonus = 0
        for k in range(0, len(res), max(1, len(res)//6)):
            rx, ry = res[k]
            if inb(nx, ny) and (rx, ry) not in obst:
                d = dist((nx, ny), (rx, ry))
                if d <= nsd:
                    any_bonus += 1
        score = ((nsd - nod), nsd, -any_bonus, abs(dx) + abs(dy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        for dx, dy in moves:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]