def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best = None
    best_sc = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        sc = (do - ds) * 100 - ds  # prioritize stealing (do>ds), then being close
        if best is None or sc > best_sc or (sc == best_sc and (tx < best[0] or (tx == best[0] and ty < best[1]))):
            best, best_sc = (tx, ty), sc

    tx, ty = best

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # choose deterministic among best-scoring immediate deltas
    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                deltas.append((dx, dy))
    if (0, 0) not in deltas:
        deltas.append((0, 0))

    def step_score(dx, dy):
        nx, ny = sx + dx, sy + dy
        # If already on a resource, stay
        if (nx, ny) in resources:
            return 10**9
        ds_new = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        return (do - ds_new) * 100 - ds_new

    best_d = None
    best_val = None
    for dx, dy in deltas:
        v = step_score(dx, dy)
        if best_d is None or v > best_val or (v == best_val and (dx, dy) < best_d):
            best_d, best_val = (dx, dy), v

    return [int(best_d[0]), int(best_d[1])]