def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is None:
            continue
        x, y = p[0], p[1]
        obs.add((int(x), int(y)))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p is None:
            continue
        x, y = p[0], p[1]
        res.append((int(x), int(y)))

    def sqdist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = moves[4]
    best_score = -10**30

    cx, cy = w // 2, h // 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        if res:
            best_adv = -10**30
            best_ds = 10**30
            found = False
            for rx, ry in res:
                ds = sqdist(nx, ny, rx, ry)
                do = sqdist(ox, oy, rx, ry)
                adv = do - ds
                if (not found) or adv > best_adv or (adv == best_adv and ds < best_ds):
                    best_adv = adv
                    best_ds = ds
                    found = True
            score = best_adv * 1000 - best_ds * 0.01
            if best_adv <= 0:
                score += -sqdist(nx, ny, cx, cy) * 0.001
        else:
            score = -sqdist(nx, ny, cx, cy) * 0.001

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move