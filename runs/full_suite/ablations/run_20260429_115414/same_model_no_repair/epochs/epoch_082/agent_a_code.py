def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    best_r = None
    best_key = None
    for rx, ry in resources:
        md = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        diff = md - od  # negative => we are ahead
        key = (diff, md, man(rx, ry, (w - 1) // 2, (h - 1) // 2), rx, ry)
        if best_key is None or key < best_key:
            best_key, best_r = key, (rx, ry)

    tx, ty = best_r

    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_t = man(nx, ny, tx, ty)
        d_opp_t = man(ox, oy, tx, ty)
        # Prefer decreasing our distance; if tied, favor moves that are farther from opponent overall.
        d_opp_here = man(nx, ny, ox, oy)
        val = (d_to_t, -d_opp_here, dx, dy)
        if best_val is None or val < best_val:
            best_val, best_move = val, [dx, dy]

    nx, ny = sx + best_move[0], sy + best_move[1]
    if not inb(nx, ny):
        return [0, 0]
    return best_move