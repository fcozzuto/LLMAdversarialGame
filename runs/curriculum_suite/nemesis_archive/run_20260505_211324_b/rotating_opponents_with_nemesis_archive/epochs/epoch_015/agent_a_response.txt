def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            obs.add((o[0], o[1]))
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            res.append((r[0], r[1]))
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick the best resource where we can arrive strictly earlier.
    best = None
    best_adv = -10**9
    for rx, ry in res:
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        adv = od - sd
        if sd == 0:
            best = (rx, ry)
            best_adv = 10**9
            break
        if sd < od:
            if adv > best_adv or (adv == best_adv and (rx + ry) < (best[0] + best[1])):
                best_adv = adv
                best = (rx, ry)

    # If no winning resource, switch to the closest resource but with an anti-race bias.
    if best is None:
        bestd = 10**9
        best = res[0]
        for rx, ry in res:
            sd = manh(sx, sy, rx, ry)
            od = manh(ox, oy, rx, ry)
            # Prefer resources that keep distance from opponent (reduce their ability to contest immediately).
            key = (sd, -od, rx, ry)
            cur = (sd, -od, rx, ry)
            if cur < (bestd, -manh(ox, oy, best[0], best[1]), best[0], best[1]):
                bestd = sd
                best = (rx, ry)

    tx, ty = best

    # Interceptor-like move: choose step that reduces our distance most while also not giving opponent a near
    # option to the same target (secondary objective).
    def opp_step_score(nx, ny):
        # After we move to (nx, ny), opponent likely moves toward the same target.
        # Estimate their best next distance to target, then minimize it as a penalty (we want to keep it high).
        best_ = 10**9
        for dx, dy in deltas:
            px, py = ox + dx, oy + dy
            if not inside(px, py) or (px, py) in obs:
                continue
            best_ = min(best_, manh(px, py, tx, ty))
        return best_

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        sd = manh(nx, ny, tx, ty)
        # Primary: minimize our distance to target.
        # Secondary: keep opponent farther from the target after their greedy step estimate.
        penalty = opp_step_score(nx, ny)
        # Also add slight repulsion from opponent when contested.
        contest = manh(nx, ny, ox, oy)
        val = (-sd * 1000) + (penalty * 10) + (contest)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]