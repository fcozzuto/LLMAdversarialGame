def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    best_move = None
    best_score = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        s = 0
        for cell in res:
            sd = dist((nx, ny), cell)
            od = dist((ox, oy), cell)
            # Prefer cells we can reach sooner, and closer cells overall
            s += (od - sd) * 10 - sd
        # Deterministic tie-break
        if s > best_score or (s == best_score and (dx, dy) < best_move):
            best_score = s
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]