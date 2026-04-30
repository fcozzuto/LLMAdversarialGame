def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if p is None:
            continue
        try:
            x, y = p
            obstacles.add((x, y))
        except Exception:
            pass

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if resources:
            best_res = 10**18
            best_adv = -10**18
            for rx, ry in resources:
                sd = dist(nx, ny, rx, ry)
                od = dist(ox, oy, rx, ry)
                adv = sd - od  # negative => we are closer
                if adv < best_adv:
                    best_adv = adv
                if sd < best_res:
                    best_res = sd
            val = (-best_adv) * 1000000 - best_res
        else:
            val = dist(nx, ny, ox, oy)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]