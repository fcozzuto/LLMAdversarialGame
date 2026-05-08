def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def is_blocked(x, y):
        return not (0 <= x < w and 0 <= y < h) or (x, y) in obstacles

    def on_resource(x, y):
        for rx, ry in resources:
            if rx == x and ry == y:
                return True
        return False

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    if on_resource(sx, sy):
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    # pick target that we can reach first; when close, choose one that is "safer" away from opponent's side
    opp_side = 1 if ox >= cx else -1
    resources_sorted = sorted(resources, key=lambda p: (p[0], p[1]))
    best = resources_sorted[0]
    best_val = -10**9
    for rx, ry in resources_sorted:
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        safety = -1 if (rx - cx) * opp_side > 0 else 1  # prefer resources away from opponent's half-plane
        val = (od - sd) * 10 + safety
        if val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best
    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            deltas.append((dx, dy))
    deltas.sort(key=lambda d: (abs(d[0]) + abs(d[1]), d[0], d[1]))

    # move choice: greedily reduce our Chebyshev distance to target; if tied, increase separation from opponent
    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if is_blocked(nx, ny):
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(nx, ny, ox, oy)
        # prefer smaller nsd; encode as larger score; plus small term to keep away from opponent
        score = -nsd * 100 + nod
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]