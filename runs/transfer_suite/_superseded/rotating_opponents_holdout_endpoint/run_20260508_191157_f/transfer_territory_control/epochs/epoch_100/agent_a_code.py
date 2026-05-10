def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    oppT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    unC = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    neigh8 = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj(setT, x, y):
        for dx, dy in neigh8:
            if (x + dx, y + dy) in setT:
                return True
        return False

    def score_pos(x, y):
        if not inb(x, y) or (x, y) in obstacles:
            return -10**9
        sc = 0
        if (x, y) in unC:
            sc += 5
        if (x, y) in selfT:
            sc += 2
        if adj(oppT, x, y):
            sc += 3
        if adj(selfT, x, y):
            sc += 1
        sc += 2 * (-(abs(x - ox) + abs(y - oy)) // 2)
        return sc

    best = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        sc = score_pos(nx, ny)
        if sc > best:
            best = sc
            best_move = [dx, dy]
    return best_move