def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    res = set((int(x), int(y)) for x, y in (observation.get("resources") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    def man(x, y, a, b):
        return abs(x - a) + abs(y - b)

    def min_dist_to(S, x, y):
        if not S:
            return 10**9
        best = 10**9
        for tx, ty in S:
            d = man(x, y, tx, ty)
            if d < best:
                best = d
        return best

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        score = 0
        if (nx, ny) in opT:
            score += 10**12
        score -= 10 * min_dist_to(opT, nx, ny)
        score -= 2 * min_dist_to(unT, nx, ny)
        if (nx, ny) in res:
            score += 100
        score -= 0.5 * man(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move