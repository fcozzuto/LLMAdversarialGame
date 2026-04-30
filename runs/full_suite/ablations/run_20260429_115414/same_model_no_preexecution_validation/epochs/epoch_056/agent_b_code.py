def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_dx, best_dy = 0, 0
    best_score = -10**18
    # Deterministic tie-break: fixed dir order already.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Prefer move that maximizes (opponent_distance - my_distance) to any resource
        best_gap = -10**9
        best_my = 10**9
        for tx, ty in resources:
            dm = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            gap = do - dm
            if gap > best_gap:
                best_gap = gap
            if dm < best_my:
                best_my = dm
        # Also slightly prefer being closer to the nearest resource.
        score = best_gap * 1000 - best_my
        if score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]