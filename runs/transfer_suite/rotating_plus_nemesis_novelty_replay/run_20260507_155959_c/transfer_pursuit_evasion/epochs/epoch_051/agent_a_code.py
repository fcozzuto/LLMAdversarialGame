def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except Exception:
            pass

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    best = None
    best_score = None

    for dx in dxs:
        for dy in dys:
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_op = abs(nx - ox) + abs(ny - oy)
            d_ctr = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
            score = (d_op, d_ctr, dx, dy)
            if best_score is None or score < best_score:
                best_score = score
                best = [dx, dy]

    if best is not None:
        return best

    for dx in dxs:
        for dy in dys:
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]

    return [0, 0]