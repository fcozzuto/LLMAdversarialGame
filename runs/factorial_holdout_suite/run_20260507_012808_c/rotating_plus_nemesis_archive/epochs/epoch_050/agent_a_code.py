def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    free_res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                free_res.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    target = None
    best = None
    for tx, ty in free_res:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Prefer resources where we can arrive strictly earlier; otherwise, pick closest to us.
        key = (0 if sd < od else 1, sd, od, tx, ty)
        if best is None or key < best:
            best = key; target = (tx, ty)

    if target is None:
        return [0, 0]

    tx, ty = target
    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(nx, ny, ox, oy)
        # Commit to target; if blocked path, keep moving to reduce target distance, and avoid letting opponent get nearer to it.
        key = (nsd, -nod, dx, dy)
        if best_key is None or key < best_key:
            best_key = key; best_move = [dx, dy]

    return best_move