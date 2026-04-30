def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obs_list = observation.get("obstacles", [])
    obstacles = set((p[0], p[1]) for p in obs_list) if obs_list else set()

    def sqd(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    target = None
    best = None
    for r in resources:
        rx, ry = r[0], r[1]
        if (rx, ry) in obstacles:
            continue
        v = sqd(ox, oy, rx, ry) - sqd(sx, sy, rx, ry)
        if best is None or v > best or (v == best and sqd(sx, sy, rx, ry) < sqd(sx, sy, target[0], target[1])):
            best = v
            target = (rx, ry)
    if target is None:
        if resources:
            target = (resources[0][0], resources[0][1])
        else:
            target = (ox, oy)

    tx, ty = target
    best_move = [0, 0]
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            my_d = sqd(nx, ny, tx, ty)
            opp_d = sqd(ox, oy, tx, ty)
            val = (opp_d - my_d, -my_d)
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]
    return best_move