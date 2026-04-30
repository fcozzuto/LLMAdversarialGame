def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set()
    for px, py in obstacles:
        obs.add((px, py))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def clamp(a, lo, hi):
        return lo if a < lo else hi if a > hi else a

    def d2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    if resources:
        best_move = (0, 0)
        best_val = None
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if nx < 0 or ny < 0 or nx >= gw or ny >= gh:
                continue
            if (nx, ny) in obs:
                continue
            val = None
            for rx, ry in resources:
                ds = d2(nx, ny, rx, ry)
                do = d2(ox, oy, rx, ry)
                v = ds - 0.6 * do
                if val is None or v < val:
                    val = v
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: move to reduce distance to opponent (interference).
    best_move = (0, 0)
    best_d = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or ny < 0 or nx >= gw or ny >= gh:
            continue
        if (nx, ny) in obs:
            continue
        dd = d2(nx, ny, ox, oy)
        if best_d is None or dd < best_d:
            best_d = dd
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]