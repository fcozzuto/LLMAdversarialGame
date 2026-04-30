def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def d2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    def nearest_dist(px, py):
        if not resources:
            return None, None
        best = None
        for rx, ry in resources:
            val = (d2(px, py, rx, ry), rx, ry)
            if best is None or val < best:
                best = val
        return best[0], (best[1], best[2])

    valid = []
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            valid.append((dx, dy, nx, ny))

    if not valid:
        return [0, 0]

    my_prev_d, _ = nearest_dist(x, y)
    opp_prev_d, _ = nearest_dist(ox, oy)

    best_mv = valid[0]
    best_val = None
    for dx, dy, nx, ny in valid:
        if resources:
            my_d, _ = nearest_dist(nx, ny)
            opp_d, _ = nearest_dist(ox, oy)
            val = (opp_d - my_d, -my_d, nx, ny, dx, dy)
        else:
            val = (d2(nx, ny, ox, oy), -d2(nx, ny, ox, oy), nx, ny, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_mv = (dx, dy, nx, ny)

    return [best_mv[0], best_mv[1]]