def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    my_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    cx = (w - 1) // 2
    cy = (h - 1) // 2

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    nearest_unclaimed_dist_now = None
    if unclaimed:
        nearest_unclaimed_dist_now = min(man(sx, sy, x, y) for (x, y) in unclaimed)

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None

    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        val = 0.0
        if (nx, ny) in my_terr:
            val += 1.0
        elif (nx, ny) in unclaimed:
            val += 5.5
        elif (nx, ny) in opp_terr:
            val += 7.0
        else:
            val += 0.2

        dcent = man(nx, ny, cx, cy)
        val += -0.05 * dcent

        if unclaimed:
            d_un = min(man(nx, ny, x, y) for (x, y) in unclaimed)
            if nearest_unclaimed_dist_now is not None:
                val += 0.8 * (nearest_unclaimed_dist_now - d_un)

        # Prefer not to get stuck on edges: mild bias to reduce distance moved from center line
        val += -0.01 * man(nx, ny, sx, sy)

        # Deterministic tie-break: fixed iteration order, then (dx,dy)
        if best is None or val > best[0] or (val == best[0] and (dx, dy) < best[1]):
            best = (val, (dx, dy))

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]