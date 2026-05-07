def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = r[0], r[1]
            if (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_target(px, py):
        best = None
        best_key = None
        for tx, ty in resources:
            ds = cheb(px, py, tx, ty)
            do = cheb(ox, oy, tx, ty)
            key = (ds - do, ds, cheb(sx, sy, tx, ty), tx, ty)
            if best_key is None or key < best_key:
                best_key = key
                best = (tx, ty)
        return best

    tx, ty = best_target(sx, sy)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_to_target = cheb(nx, ny, tx, ty)
            d_opp = cheb(nx, ny, ox, oy)
            # Primary: get closer to target, Secondary: keep away from opponent, Tertiary: deterministic order
            candidates.append((d_to_target, -d_opp, dx, dy))
    candidates.sort()
    return [candidates[0][2], candidates[0][3]] if candidates else [0, 0]