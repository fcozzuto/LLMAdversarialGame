def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    self_ter = set(tuple(p) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_ter = set(tuple(p) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    frontier = []
    for x, y in self_ter:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                frontier.append((nx, ny))
    frontier = list(dict.fromkeys(frontier))
    target = None
    if frontier:
        target = min(frontier, key=lambda p: (dist((sx, sy), p), p[0], p[1]))
    else:
        near_unclaimed = []
        for p in unclaimed:
            if dist((sx, sy), p) <= 3:
                near_unclaimed.append(p)
        if near_unclaimed:
            target = min(near_unclaimed, key=lambda p: (dist((sx, sy), p), p[0], p[1]))

    if target is None:
        target = (ox, oy)

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            sc = -10**9
        else:
            sc = 0
            if (nx, ny) in unclaimed:
                sc += 7
            if (nx, ny) in self_ter:
                sc += 2
            if (nx, ny) in opp_ter:
                sc -= 4
            sc += -dist((nx, ny), target)
            sc -= 2 if dist((nx, ny), (ox, oy)) <= 1 else 0
        if (sc, dx, dy) > best:
            best = (sc, dx, dy)
    return [int(best[1]), int(best[2])]