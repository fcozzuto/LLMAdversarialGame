def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((int(p[0]), int(p[1])))
        except:
            pass

    sr = str(observation.get("self_role", "")).lower()
    evader = ("evad" in sr)

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def safe(x, y): return inb(x, y) and (x, y) not in obs

    bx = by = 0
    if safe(sx, sy):
        bx, by = sx, sy

    best = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score = d if evader else -d
        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    if safe(sx + best_move[0], sy + best_move[1]):
        return [int(best_move[0]), int(best_move[1])]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if safe(nx, ny):
            return [int(dx), int(dy)]
    return [0, 0]