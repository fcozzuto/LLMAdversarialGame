def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    if not resources:
        dx = 0
        dy = 0
        if sx < ox:
            dx = 1
        elif sx > ox:
            dx = -1
        elif sy < oy:
            dy = 1
        elif sy > oy:
            dy = -1
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [dx, dy]
        return [0, 0]

    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        my_d = 10**9
        opp_d = 10**9
        touch = 0
        for r in resources:
            rx, ry = r[0], r[1]
            dmy = cheb(nx, ny, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            if dmy < my_d:
                my_d = dmy
            if dop < opp_d:
                opp_d = dop
            if dmy == 0:
                touch = 1
                break
        val = (opp_d - my_d) * 100 - my_d
        if touch:
            val += 10**7
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move