def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def to_set(v):
        s = set()
        if not v:
            return s
        for p in v:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inb(x, y):
                    s.add((x, y))
        return s

    obstacles = to_set(observation.get("obstacles"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    opp_t = to_set(observation.get("opponent_territory"))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    prio = set()
    for (x, y) in opp_t:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                prio.add((nx, ny))

    if prio:
        tx, ty = sorted(prio)[0]
    elif unclaimed:
        tx, ty = sorted(unclaimed, key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))[0]
    else:
        tx, ty = ox, oy

    best = None
    best_score = -10**9
    best_i = 10
    for i, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in unclaimed:
            score += 8
        for adx, ady in dirs:
            ax, ay = nx + adx, ny + ady
            if inb(ax, ay) and (ax, ay) in opp_t:
                score += 3
                break
        score += 3 - man(nx, ny, tx, ty)
        score += 1 if man(nx, ny, ox, oy) < man(sx, sy, ox, oy) else 0
        if score > best_score or (score == best_score and i < best_i):
            best_score = score
            best_i = i
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best