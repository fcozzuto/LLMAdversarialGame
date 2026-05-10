def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    own = set()
    for p in observation.get("self_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            own.add((int(p[0]), int(p[1])))

    opp = set()
    for p in observation.get("opponent_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp.add((int(p[0]), int(p[1])))

    targets = []
    for p in observation.get("unclaimed_cells", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            targets.append((int(p[0]), int(p[1])))
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            targets.append((int(p[0]), int(p[1])))
    if not targets:
        targets = [(ox, oy)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_to(x, y):
        best = 10**9
        for tx, ty in targets:
            if (tx, ty) in obstacles:
                continue
            d = abs(x - tx) + abs(y - ty)
            if d < best:
                best = d
        s = -best
        if (x, y) in opp:
            s += 3
        if (x, y) in own:
            s -= 1
        return s

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best_move = (0, 0)
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        sc = score_to(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]