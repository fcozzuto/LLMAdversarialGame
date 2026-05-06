def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set(obs_list if isinstance(obs_list, (list, set, tuple)) else [])
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = -10**18
    best_move = [0, 0]
    has_res = len(resources) > 0

    for dx, dy in deltas:
        x, y = sx + dx, sy + dy
        if not inb(x, y):
            continue
        if (x, y) in obstacles:
            continue

        if has_res:
            dnr = 10**9
            for r in resources:
                if isinstance(r, (list, tuple)) and len(r) >= 2:
                    dnr = min(dnr, md(x, y, r[0], r[1]))
            dpo = md(x, y, ox, oy)
            score = -dnr * 10 - dpo + (dx == 0 and dy == 0) * 0.1
        else:
            dpo = md(x, y, ox, oy)
            score = dpo * 10 - ((x - (w - 1) / 2.0) ** 2 + (y - (h - 1) / 2.0) ** 2) * 0.001

        if score > best:
            best = score
            best_move = [dx, dy]

    return best_move