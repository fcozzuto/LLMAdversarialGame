def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return max(abs(x2 - x1), abs(y2 - y1))

    def step_toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        return step_toward(tx, ty)

    res = [tuple(r) for r in resources]
    best = None
    best_key = (-10**18, 10**18, 10**18)  # (adv, -self_d, self_d)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Compute best contest value: prioritize winning a resource this turn/soon by advantage,
        # then being closer to something, while avoiding moving into poor local contest.
        best_adv = -10**18
        best_self_d = 10**18
        for rx, ry in res:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            adv = (do - ds)  # positive means we are closer (in chebyshev metric)
            # Small tie preferences: prefer nearer resource (lower ds) and slight preference to those far from opponent.
            key_adv = adv
            if key_adv > best_adv or (key_adv == best_adv and ds < best_self_d):
                best_adv, best_self_d = key_adv, ds

        # If we can directly step onto a resource, strongly prefer it.
        direct = 1 if any(nx == rx and ny == ry for rx, ry in res) else 0
        adv_final = best_adv + 1000 * direct
        key = (adv_final, -best_self_d, best_self_d)
        if key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]