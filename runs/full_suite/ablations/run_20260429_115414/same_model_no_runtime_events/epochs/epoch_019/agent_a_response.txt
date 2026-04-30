def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    res_set = set()
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
                res_set.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if resources:
        tx, ty = min(resources, key=lambda r: abs(r[0] - sx) + abs(r[1] - sy))
    else:
        tx, ty = (w // 2, h // 2)
        if (sx, sy) == (tx, ty) and resources:
            tx, ty = resources[0]

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_dist_now = abs(sx - ox) + abs(sy - oy)

    best = (0, 0)
    best_score = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        d_self = abs(nx - tx) + abs(ny - ty)
        opp_d = abs(nx - ox) + abs(ny - oy)

        score = -d_self
        if (nx, ny) in res_set:
            score += 1000
        else:
            score += 0.15 * (opp_d - opp_dist_now)  # stay farther from opponent if not collecting

        # If moving puts opponent closer to the target than we are, penalize
        if resources:
            opp_target_d = abs(ox - tx) + abs(oy - ty)
            # approximate worst-case opponent reply: if we move away, opponent likely advances
            if opp_target_d > 0:
                score -= 0.05 * (abs(nx - tx) + abs(ny - ty)) / (opp_target_d + 1)

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]