def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    # pick best target by "who gets there first"
    best_targets = []
    for r in res:
        rx, ry = r
        our_d = md(sx, sy, rx, ry)
        opp_d = md(ox, oy, rx, ry)
        advantage = opp_d - our_d
        best_targets.append((advantage, -our_d, -opp_d, rx, ry))
    best_targets.sort(reverse=True)
    _, _, _, tx, ty = best_targets[0]

    cur_on_res = (sx, sy) in set(res)
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        our_after = md(nx, ny, tx, ty)
        opp_to_target = md(ox, oy, tx, ty)
        advantage_after = opp_to_target - our_after
        # if we move onto any resource, add a strong boost
        collect_boost = 0
        if (nx, ny) in set(res):
            collect_boost = 1000
        # mild preference for reducing distance to avoid getting swept
        score = collect_boost + advantage_after * 50 - our_after * 2 - md(nx, ny, ox, oy) * 0.1
        if cur_on_res:
            score += 10
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]