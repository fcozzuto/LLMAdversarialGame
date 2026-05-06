def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dsq(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx*dx + dy*dy

    if resources:
        best_r = None
        best_d = 10**18
        for r in resources:
            rx, ry = r[0], r[1]
            d = dsq(sx, sy, rx, ry)
            if d < best_d:
                best_d = d
                best_r = (rx, ry)
        tx, ty = best_r
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            val = -dsq(nx, ny, tx, ty) - 0.001*dsq(nx, ny, ox, oy)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    cx, cy = w // 2, h // 2
    best_move = (0, 0)
    best_d = 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d = dsq(nx, ny, cx, cy)
        if d < best_d:
            best_d = d
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]