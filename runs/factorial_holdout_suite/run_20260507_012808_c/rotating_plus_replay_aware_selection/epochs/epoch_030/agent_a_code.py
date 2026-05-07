def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def man(x1, y1, x2, y2):
        ax = x1 - x2
        ay = y1 - y2
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    ox, oy = observation["opponent_position"]

    def score_move(dx, dy, nx, ny):
        # Race score: maximize our advantage (opponent - self) to the best reachable resource.
        best_adv = -10**9
        # Small tie-break: prefer collecting sooner (smaller self distance) and avoid moving into tight obstacle neighborhoods.
        best_time = 10**9
        adj_obst = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    adj_obst += 1
        for rx, ry in resources:
            dself = man(nx, ny, rx, ry)
            dopp = man(ox, oy, rx, ry)
            # Encourage not letting opponent be closer than us.
            adv = dopp - dself
            if adv > best_adv or (adv == best_adv and dself < best_time):
                best_adv = adv
                best_time = dself
        # If adjacent to a resource, heavily prioritize.
        near_bonus = -best_time
        return best_adv * 1000 + near_bonus - adj_obst * 3 + (1 if (dx == 0 and dy == 0) else 0) * -1

    # Deterministic tie-break: fixed order over dx,dy.
    fixed_order = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            fixed_order.append((dx, dy))

    best = None
    best_s = None
    for dx, dy, nx, ny in moves:
        s = score_move(dx, dy, nx, ny)
        if best_s is None or s > best_s:
            best_s = s
            best = (dx, dy)
        elif s == best_s:
            for odx, ody in fixed_order:
                if (odx, ody) == (dx, dy):
                    best = (dx, dy)
                    break

    return [best[0], best[1]]