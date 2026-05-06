def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])

    obstacles = observation.get("obstacles", None) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources_raw = observation.get("resources", None) or []
    res = []
    for r in resources_raw:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obst)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_resource_metric(px, py):
        if not res:
            return 0, None
        best = None
        # Prefer resources where self is relatively closer than opponent
        for rx, ry in res:
            sd = man(px, py, rx, ry)
            od = man(ox, oy, rx, ry)
            gap = od - sd  # positive means self closer
            # Tie-break: closer to resource and not too far from mid
            mid_bias = abs(rx - (w // 2)) + abs(ry - (h // 2))
            metric = gap * 10 - sd - 0.01 * mid_bias
            if best is None or metric > best[0]:
                best = (metric, (rx, ry))
        return best[0], best[1]

    best_move = (None, -10**9)
    tie_order = 0
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        on_res = 1 if (nx, ny) in set(res) else 0

        metric, target = best_resource_metric(nx, ny)
        if target is None:
            rsd = abs(nx - w // 2) + abs(ny - h // 2)
            opp_d = abs(nx - ox) + abs(ny - oy)
            score = -rsd + 0.2 * opp_d + on_res * 20
        else:
            rx, ry = target
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Also mildly discourage moving away from opponent when we can't win the target
            score = (od - sd) * 2.2 + metric * 0.02 + on_res * 25 - 0.05 * sd
            # If opponent would immediately step onto the target, attempt to keep gap
            opp_target_here = (abs(ox - rx) <= 1 and abs(oy - ry) <= 1) and man(ox, oy, rx, ry) <= 1
            if opp_target_here and on_res == 0:
                score -= 6

        # Deterministic tie-break: prefer staying still, then lexicographic dx,dy
        stay_bias = 1 if (dx == 0 and dy == 0) else 0
        score += stay_bias * 0.001 + tie_order * 0.0
        if score > best_move[1]:
            best_move = ((dx, dy), score)
        tie_order += 1

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0][0]), int(best_move[0][1])]