def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    rem = int(observation.get("remaining_resource_count", len(res)) or len(res))
    endgame = 1.9 if rem <= 4 else (1.2 if rem <= 8 else 1.0)

    def best_value(px, py):
        bestv = -10**18
        for x, y in res:
            sd = abs(x - px) + abs(y - py)
            od = abs(x - ox) + abs(y - oy)
            adv = (od - sd)
            v = adv * (10.0 * endgame) - (0.25 * sd) + (1.0 / (1.0 + sd))
            if v > bestv:
                bestv = v
        return bestv

    best_move = [0, 0]
    best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            v = best_value(nx, ny)
            # Small deterministic preference for closer to a target to stabilize
            sd_self = min(abs(x - nx) + abs(y - ny) for x, y in res)
            tie = (-(sd_self), dx, dy)
            score = (v, tie)
            if score > (best_score, (0, best_move[0], best_move[1])):
                best_score = v
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]