def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    opp_dist_cache = {}
    for r in resources:
        opp_dist_cache[r] = cheb(r[0], r[1], ox, oy)

    best_r = resources[0]
    best_s = -10**18
    for r in resources:
        du = cheb(sx, sy, r[0], r[1])
        do = opp_dist_cache[r]
        # Prefer resources opponent is farther from, but still reachable.
        # Deterministic tie-break by coordinates.
        s = (do - du) * 100 - du
        if s > best_s or (s == best_s and (r[0], r[1]) < (best_r[0], best_r[1])):
            best_s, best_r = s, r

    tx, ty = best_r
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        # If multiple moves keep similar progress, move away from opponent to break ties.
        d_opp = cheb(nx, ny, ox, oy)
        val = -d_to_t * 10 + d_opp
        if val > best_val:
            best_val, best_move = val, (dx, dy)
    return [int(best_move[0]), int(best_move[1])]