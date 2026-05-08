def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score, best_move = 10**18, (0, 0)

    def blocked_neighbors(nx, ny):
        c = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                ax, ay = nx + ex, ny + ey
                if inb(ax, ay) and (ax, ay) in obs:
                    c += 1
        return c

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        adx, ady = abs(nx - ox), abs(ny - oy)
        man = adx + ady
        # Strongly prefer moves that reduce Manhattan distance; if tied, prefer reducing coordinate spread.
        coord = (adx, ady)  # deterministic lex tie-break via tuple
        # Discourage stepping near obstacles, especially when it doesn't immediately reduce distance.
        near = blocked_neighbors(nx, ny)
        improved = 1 if man < (abs(sx - ox) + abs(sy - oy)) else 0

        score = (man * 100 + (0 if improved else 50) + near * 12) * 10 + coord[0] * 2 + coord[1]
        if score < best_score:
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]