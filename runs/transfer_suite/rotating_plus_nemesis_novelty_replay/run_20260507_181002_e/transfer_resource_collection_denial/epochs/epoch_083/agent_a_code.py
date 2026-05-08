def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_set = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]
    if not resources:
        return [0, 0]

    best = None
    best_score = -10**18
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        our_best = 10**9
        opp_best = 10**9
        our_best_idx = 0
        for i, (rx, ry) in enumerate(resources):
            d1 = abs(nx - rx) + abs(ny - ry)
            if d1 < our_best:
                our_best = d1
                our_best_idx = i
            d2 = abs(ox - rx) + abs(oy - ry)
            if d2 < opp_best:
                opp_best = d2
        score = (opp_best - our_best)
        rx, ry = resources[our_best_idx]
        score -= 0.01 * (abs(nx - rx) + abs(ny - ry))
        if score > best_score:
            best_score = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]