def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    try:
        sx = int(sx)
        sy = int(sy)
    except:
        sx, sy = 0, 0
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                obstacles.add((int(p[0]), int(p[1])))
            except:
                pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_value(x, y):
        if not inb(x, y) or (x, y) in obstacles:
            return -10**9
        unclaimed = observation.get("unclaimed_cells", []) or []
        for c in unclaimed:
            if isinstance(c, (list, tuple)) and len(c) >= 2:
                try:
                    if int(c[0]) == x and int(c[1]) == y:
                        return 1000
                except:
                    pass
        opp = observation.get("opponent_position", [None, None]) or [None, None]
        try:
            ox, oy = int(opp[0]), int(opp[1])
            if x == ox and y == oy:
                return 200
        except:
            pass
        return 0

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp = observation.get("opponent_position", [None, None]) or [None, None]
    try:
        ox, oy = int(opp[0]), int(opp[1])
    except:
        ox, oy = sx, sy

    unclaimed = observation.get("unclaimed_cells", []) or []
    targets = []
    for c in unclaimed:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            try:
                x, y = int(c[0]), int(c[1])
            except:
                continue
            if inb(x, y) and (x, y) not in obstacles:
                targets.append((x, y))
    if not targets:
        targets = [(ox, oy)]

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = cell_value(nx, ny)
        dist = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
        score = v - dist
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]