def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    selfT = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opT = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unT = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def adj_count(x, y, S):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in S:
                    c += 1
        return c

    best = None
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy  # engine keeps in place on invalid move
            dx, dy = 0, 0
        score = 0
        if (nx, ny) in opT:
            score += 220 + 10 * adj_count(nx, ny, unT)
        elif (nx, ny) in unT:
            score += 140 + 15 * adj_count(nx, ny, unT) + 6 * adj_count(nx, ny, selfT)
        else:
            score += 10 * adj_count(nx, ny, unT) + 4 * adj_count(nx, ny, selfT)
        score += 3 * (abs(nx - (w - 1)) + abs(ny - (h - 1)))  # keep pushing away from own corner to sweep
        score -= 2 * (abs(nx - ox) + abs(ny - oy))  # avoid being too close to sweeper
        if score > best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best