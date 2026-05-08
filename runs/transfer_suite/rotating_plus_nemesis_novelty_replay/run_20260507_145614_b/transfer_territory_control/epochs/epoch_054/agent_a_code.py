def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    best_score = -10**18

    opp_dist_cache = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        score = -2 * d_opp

        if resources:
            best_res = 10**9
            for rx, ry in resources:
                d = abs(nx - rx) + abs(ny - ry)
                if d < best_res:
                    best_res = d
            score += 20 / (1 + best_res)
        else:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score += -0.01 * (abs(nx - cx) + abs(ny - cy))

        if nx == ox and ny == oy:
            score -= 1000000
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best