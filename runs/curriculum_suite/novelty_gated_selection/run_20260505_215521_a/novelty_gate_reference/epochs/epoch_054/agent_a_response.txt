def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = (w - 1 - ox), (h - 1 - oy)
        bestm = (0, 0)
        bestv = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                v = cheb(nx, ny, tx, ty)
                if v < bestv:
                    bestv = v
                    bestm = (dx, dy)
        return [bestm[0], bestm[1]]

    best_res = None
    best_key = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Denier-counter: choose resource where we have maximum timing advantage (min ds-do)
        key = (ds - do, ds, (tx + ty) & 1)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (tx, ty)

    tx, ty = best_res
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    desired = (dx0, dy0)
    # Prefer move that heads directly to chosen resource; if blocked, pick best local alternative
    bestm = (0, 0)
    bestv = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = cheb(nx, ny, tx, ty)
        direct = 0 if (dx, dy) == desired else 1
        # Also discourage stepping too close to opponent's chosen target resource by timing (minor)
        opp_dist = cheb(nx, ny, ox, oy)
        v = (direct, dist, opp_dist)
        if v < bestv if isinstance(bestv, tuple) else True:
            bestv = v
            bestm = (dx, dy)

    return [bestm[0], bestm[1]]