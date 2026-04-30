def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        dx = 0
        dy = 0
        return [dx, dy]
    def clamp_step(x, y, nx, ny):
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            return [x - nx, y - ny]
        if (nx, ny) in obstacles:
            return [0, 0]
        return [nx - x, ny - y]
    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dy = ay - by
        return abs(dx) + abs(dy)
    def best_resource():
        best = None
        best_key = None
        for r in resources:
            rx, ry = r
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            score = (do - ds)  # prefer resources opponent is farther from
            key = (score, -ds, -abs(rx - (w - 1 - sx)) - abs(ry - (h - 1 - sy)), rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best
    target = best_resource()
    tx, ty = target
    dx = 0; dy = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    if ty > sy: dy = 1
    elif ty < sy: dy = -1
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles or nx < 0 or ny < 0 or nx >= w or ny >= h:
        candidates = []
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                cx, cy = sx + ddx, sy + ddy
                if cx < 0 or cy < 0 or cx >= w or cy >= h: 
                    continue
                if (cx, cy) in obstacles:
                    continue
                cs = dist((cx, cy), (tx, ty)) - 0.15 * dist((cx, cy), (ox, oy))
                candidates.append((( -cs, cx, cy), [ddx, ddy]))
        candidates.sort(reverse=True)
        if candidates:
            return candidates[0][1]
        return [0, 0]
    return [dx, dy]