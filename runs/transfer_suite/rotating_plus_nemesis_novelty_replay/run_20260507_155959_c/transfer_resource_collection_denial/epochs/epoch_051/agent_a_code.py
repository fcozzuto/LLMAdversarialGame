def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(a, b, c, d): return abs(a - c) + abs(b - d)
    if (sx, sy) in obs:
        return [0, 0]

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    # Opponent likely targets nearest remaining resource (ties deterministic).
    res_sorted = sorted(res)
    best_opp = None; best_opp_d = 10**9
    for rx, ry in res_sorted:
        d = md(ox, oy, rx, ry)
        if d < best_opp_d:
            best_opp_d = d; best_opp = (rx, ry)

    # Predict opponent next position under greedy shortest-distance move to its target.
    tx, ty = best_opp
    opp_steps = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                nx, ny = ox, oy
            else:
                nx, ny = ox + dx, oy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            opp_steps.append((md(nx, ny, tx, ty), nx, ny))
    opp_steps.sort()
    nox, noy = opp_steps[0][1], opp_steps[0][2]

    # Choose our next move to either race for resources or intercept the predicted next cell.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            if (dx, dy) != (0, 0):
                pass
            # Intercept value: prefer landing on opponent next cell or near it.
            intercept = -md(nx, ny, nox, noy)

            # Racing value: prefer resources where we are closer (steal) and especially the opponent's target.
            race_best = -10**9
            for rx, ry in res_sorted:
                sd = md(nx, ny, rx, ry)
                od = md(nox, noy, rx, ry)
                # Positive if we are effectively ahead in the race after their next move.
                v = (od - sd)
                if (rx, ry) == best_opp:
                    v += 1  # small extra focus on their immediate target
                if v > race_best:
                    race_best = v

            # Secondary: go toward the closest "good" resource to avoid deadlocks.
            closest = min(md(nx, ny, rx, ry) for rx, ry in res_sorted)
            candidates.append((intercept, race_best, -closest, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(reverse=True)
    dx, dy = candidates[0][3], candidates[0][4]
    return [int(dx), int(dy)]