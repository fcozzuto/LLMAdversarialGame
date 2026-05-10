def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    res = []
    for x, y in resources:
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def obs_pen(x, y):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obs:
                    pen += 1
        return pen

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        my_pen = obs_pen(nx, ny)
        val = 0
        # Choose resource where we beat opponent in race to arrival
        for rx, ry in res:
            self_t = cheb(nx, ny, rx, ry)
            opp_t = cheb(ox, oy, rx, ry)
            race = opp_t - self_t  # positive if we arrive earlier
            # Prefer earlier capture, then closer, while avoiding risky obstacle adjacency
            cand = race * 100 - self_t * 3 - my_pen * 2
            if rx == nx and ry == ny:
                cand += 10000
            if cand > val:
                val = cand
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move