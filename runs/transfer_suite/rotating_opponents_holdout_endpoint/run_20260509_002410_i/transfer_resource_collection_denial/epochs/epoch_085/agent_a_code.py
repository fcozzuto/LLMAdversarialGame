def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_list:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best_moves = []
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    nearest = []
    for r in resources:
        if r and len(r) >= 2:
            tx = int(r[0]); ty = int(r[1])
            if 0 <= tx < w and 0 <= ty < h:
                nearest.append((tx, ty))
    if not nearest:
        # If no resources known, keep moving away from opponent if possible
        best = None
        bestd = -10**9
        for dx, dy, nx, ny in candidates:
            d = man(nx, ny, ox, oy)
            if d > bestd:
                bestd = d
                best = (dx, dy)
        return [int(best[0]), int(best[1])] if best else [0, 0]

    best = None
    best_tuple = None
    for dx, dy, nx, ny in candidates:
        dmin = min(man(nx, ny, tx, ty) for tx, ty in nearest)
        do = man(nx, ny, ox, oy)
        # Prefer shorter distance to nearest resource; tie-break by staying farther from opponent.
        t = (-dmin, -do, dx, dy)
        if best_tuple is None or t > best_tuple:
            best_tuple = t
            best = (dx, dy)
    return [int(best[0]), int(best[1])] if best else [0, 0]