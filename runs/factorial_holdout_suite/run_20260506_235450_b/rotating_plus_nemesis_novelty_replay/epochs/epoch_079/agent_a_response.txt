def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            x, y = p
            obstacles.add((x, y))
        except:
            pass

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = (ox is not None and oy is not None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-10**18, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = -md((nx, ny), (cx, cy))
            if sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    # Precompute opponent distances to resources (if visible)
    opp_dist = {}
    for r in resources:
        rx, ry = r
        if opp_exists:
            opp_dist[(rx, ry)] = abs(rx - ox) + abs(ry - oy)
        else:
            opp_dist[(rx, ry)] = 10**9

    best_total, best_dx, best_dy = -10**18, 0, 0
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Choose the resource that gives the biggest advantage from (nx, ny)
        best_adv = -10**18
        best_self_d = 10**18
        for r in resources:
            rx, ry = r
            self_d = abs(rx - nx) + abs(ry - ny)
            adv = opp_dist[(rx, ry)] - self_d
            # Prefer clearly winning the race; tie-break by being closer
            if adv > best_adv or (adv == best_adv and self_d < best_self_d):
                best_adv = adv
                best_self_d = self_d

        # Strongly encourage winning races; slightly penalize wandering
        total = best_adv * 100 - best_self_d
        if total > best_total:
            best_total, best_dx, best_dy = total, dx, dy

    return [best_dx, best_dy]