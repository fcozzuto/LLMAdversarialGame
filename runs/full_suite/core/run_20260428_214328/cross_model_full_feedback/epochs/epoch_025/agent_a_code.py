def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    w, h = int(w), int(h)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set((int(p[0]), int(p[1])) for p in obstacles)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    resources = observation.get("resources", []) or []
    if resources:
        rs = [(int(p[0]), int(p[1])) for p in resources]
        best = None
        best_key = None
        for dx, dy, nx, ny in legal:
            our = (nx, ny)
            min_adv = 10**9
            best_res_dist = 10**9
            for r in rs:
                d_our = cheb(our, r)
                d_opp = cheb((ox, oy), r)
                adv = d_opp - d_our
                if adv < min_adv:
                    min_adv = adv
                if d_our < best_res_dist:
                    best_res_dist = d_our
            # Prefer higher minimum advantage; tie-breaker: closer to some resource; then farther from opponent
            oppd = cheb(our, (ox, oy))
            key = (min_adv, -best_res_dist, oppd)
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    # No visible resources: expand from opponent, deterministic tie-break by fewer steps to center-ish
    cx, cy = w // 2, h // 2
    best = None
    best_key = None
    for dx, dy, nx, ny in legal:
        our = (nx, ny)
        oppd = cheb(our, (ox, oy))
        center = cheb(our, (cx, cy))
        key = (oppd, -center)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)
    return [best[0], best[1]]