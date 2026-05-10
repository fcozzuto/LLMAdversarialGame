def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if len(p) >= 2)
    selfT = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if len(p) >= 2)
    opT = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if len(p) >= 2)
    unT = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if len(p) >= 2)
    unT -= obstacles

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_count(x, y, S):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in S:
                    c += 1
        return c

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        score = 0
        if (nx, ny) in opT:
            score += 1000
        score += 5 * adj_count(nx, ny, opT)
        score += 2 * adj_count(nx, ny, unT)
        if (nx, ny) in selfT:
            score -= 1  # slight discourage self-wandering
        score -= 3 * adj_count(nx, ny, obstacles)
        if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))
    return [best[1][0], best[1][1]]