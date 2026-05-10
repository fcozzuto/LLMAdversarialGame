def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    un = set((int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2)

    my_terr = observation.get("self_territory") or []
    my = set((int(p[0]), int(p[1])) for p in my_terr if isinstance(p, (list, tuple)) and len(p) >= 2)

    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    targets = []
    if my:
        for x, y in my:
            for dx, dy in dirs4 + [(-1,-1),(-1,1),(1,-1),(1,1)]:
                nx, ny = x + dx, y + dy
                if ok(nx, ny) and (nx, ny) in un:
                    targets.append((nx, ny))
    if not targets:
        targets = list(un)

    def score(x, y):
        # Prefer moving toward targets; penalize moving toward opponent.
        bestd = 10**9
        for tx, ty in targets[:60]:
            d = abs(tx - x) + abs(ty - y)
            if d < bestd:
                bestd = d
        if bestd == 10**9:
            bestd = 0
        return bestd * 10 - (abs(ox - x) + abs(oy - y))

    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = score(nx, ny)
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]