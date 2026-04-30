def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def nearest_dist(px, py, targets):
        if not targets:
            return 10**9
        best = 10**9
        for tx, ty in targets:
            d = abs(tx - px) + abs(ty - py)
            if d < best:
                best = d
        return best

    if resources:
        # Focus on opponent's nearest resource to contest it directly.
        opp_target_dist = 10**9
        opp_target = None
        for tx, ty in resources:
            d = abs(tx - ox) + abs(ty - oy)
            if d < opp_target_dist:
                opp_target_dist = d
                opp_target = (tx, ty)
        if opp_target is None:
            opp_target = resources[0]
    else:
        opp_target = None

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_opp = abs(nx - ox) + abs(ny - oy)
        if opp_target is not None:
            tx, ty = opp_target
            d_target = abs(tx - nx) + abs(ty - ny)
        else:
            d_target = nearest_dist(nx, ny, resources)

        # Score: prioritize reaching the contested target, keep some distance from opponent, prefer center slightly.
        center_pen = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        score = (-d_target * 10.0) + (d_opp * 0.35) - (center_pen * 0.02)

        # Deterministic tie-breaking via dir iteration order
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [int(dx), int(dy)]