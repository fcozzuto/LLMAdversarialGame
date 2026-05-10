def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    sr = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in sr) or ("runner" in sr) or ("escape" in sr)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free_neighbors(x, y):
        c = 0
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        fn = free_neighbors(nx, ny)
        # pursuer: minimize distance; reward mobility
        # evader: maximize distance; reward mobility and avoid cramped spots
        if is_evader:
            val = d2 * 10 + fn
        else:
            val = -d2 * 10 + fn
        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best, best_val = (dx, dy), val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]