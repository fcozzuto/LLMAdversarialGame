def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b, x, y):
        d = a - x
        if d < 0: d = -d
        e = b - y
        if e < 0: e = -e
        return d + e

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Diversified plan: prioritize "low contest" resources (far from opponent), then ensure our distance is small.
    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        own_best = 10**9
        opp_best = -1
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Want high opponent distance and low our distance.
            # Two-stage: maximize (od - 1.1*sd), tie-break by smaller sd, then higher od.
            key = (od - 11/10 * sd, -sd, od)
            # Keep best target under this move
            if key > (own_best, -own_best, opp_best):
                own_best = key[0]
                opp_best = key[2]
        # Evaluate move by the best target we can claim next; also slightly penalize moving away from any resource.
        min_sd = min(man(nx, ny, rx, ry) for rx, ry in resources)
        opp_avg_d = sum(man(ox, oy, rx, ry) for rx, ry in resources) / max(1, len(resources))
        key = (own_best, -opp_avg_d, -min_sd, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]] if best_move else [0, 0]