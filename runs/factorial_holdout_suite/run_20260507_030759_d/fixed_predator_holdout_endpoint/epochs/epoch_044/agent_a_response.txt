def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set(map(tuple, obstacles))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best_r = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        risk = 0
        for ax, ay in obstacles:
            ddx = rx - ax
            ddy = ry - ay
            d = abs(ddx) if abs(ddx) > abs(ddy) else abs(ddy)
            if d == 0:
                risk += 10**6
            elif d == 1:
                risk += 25
            elif d == 2:
                risk += 8
        key = (od - sd, -sd, -risk)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        self_d = abs(tx - nx) + abs(ty - ny)
        opp_d = abs(tx - ox) + abs(ty - oy)
        denier_gain = (abs(tx - ox) + abs(ty - oy)) - opp_d  # usually 0; keep structure
        obs_near = 0
        for ax, ay in obstacles:
            dd = abs(nx - ax) if abs(nx - ax) > abs(ny - ay) else abs(ny - ay)
            if dd == 1:
                obs_near += 6
            elif dd == 0:
                obs_near += 10**6
        score = (1000 - self_d) + 3 * denier_gain - obs_near
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move