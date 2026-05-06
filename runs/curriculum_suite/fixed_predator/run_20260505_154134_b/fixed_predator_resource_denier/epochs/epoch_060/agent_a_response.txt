def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Prefer manhattan distance for resource denial patterns
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx = (sum(r[0] for r in resources) / len(resources)) if resources else (w - 1) / 2
    cy = (sum(r[1] for r in resources) / len(resources)) if resources else (h - 1) / 2

    if not resources:
        tx, ty = int(cx), int(cy)
        best = [0, 0]
        bestv = -10**9
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = -(abs(nx - tx) + abs(ny - ty)) - 0.01 * dist((nx, ny), (ox, oy))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        self_pos = (nx, ny)

        # Denial-aware: pick move that maximizes our reach advantage over the best target.
        best_adv = -10**9
        best_my_dist = 10**9
        best_opp_dist = 10**9
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            sd = dist(self_pos, (rx, ry))
            od = dist((ox, oy), (rx, ry))
            adv = od - sd  # positive means we can arrive no later than opponent (in manhattan)
            # Favor positive/large adv first, then closer to the target for stability
            if adv > best_adv or (adv == best_adv and sd < best_my_dist) or (adv == best_adv and sd == best_my_dist and od < best_opp_dist):
                best_adv = adv
                best_my_dist = sd
                best_opp_dist = od

        # If we're behind on all targets, still choose move that reduces our best distance.
        centroid_bias = -0.02 * (abs(nx - cx) + abs(ny - cy))
        opp_threat = -0.01 * dist(self_pos, (ox, oy))  # slight pressure to not drift into opponent
        # Strongly weight advantage so behavior changes deterministically vs pure "go-to"
        val = 10.0 * best_adv - 0.5 * best_my_dist + centroid_bias + opp_threat
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move