def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    opp_terr = set()
    for p in observation.get("opponent_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))
    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def adj4(x, y):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                yield nx, ny

    frontier = []
    unobs = unclaimed if unclaimed else []
    for x, y in unobs:
        if (x, y) in obstacles: 
            continue
        if any((ax, ay) in opp_terr for ax, ay in adj4(x, y)):
            cnt = 0
            for ax, ay in adj4(x, y):
                if (ax, ay) in opp_terr: cnt += 1
            frontier.append((cnt, x, y))
    frontier.sort(reverse=True)
    target = None
    if frontier:
        _, tx, ty = frontier[0]
        target = (tx, ty)
    elif opp_terr:
        tx, ty = min(opp_terr, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
        target = (tx, ty)
    else:
        target = (w // 2, h // 2)

    best_move = (0, 0)
    best_val = -10**18
    tx, ty = target
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        dist = abs(nx - tx) + abs(ny - ty)
        cap = 1 if (nx, ny) in opp_terr else 0
        near_opp = 0
        for ax, ay in adj4(nx, ny):
            if (ax, ay) in opp_terr:
                near_opp += 1
        block = 0
        for ax, ay in adj4(nx, ny):
            if (ax, ay) in obstacles:
                block += 1
        val = (cap * 200) + (near_opp * 18) + (block * 2) - dist
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]