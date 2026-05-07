def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)
    ox, oy = observation.get("opponent_position", (None, None))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            res.append((r[0], r[1]))
    if not res:
        # Fall back: head to closest resource-like corner (deterministic), avoid obstacles
        goal = (0, 0) if (sx + sy) % 2 == 0 else (w - 1, h - 1)
        dxs = (-1, 0, 1)
        best = (-10**18, 0, 0)
        for dx in dxs:
            for dy in dxs:
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                sc = -abs(nx - goal[0]) - abs(ny - goal[1])
                if sc > best[0]:
                    best = (sc, dx, dy)
        return [best[1], best[2]]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if ox is None or oy is None:
        ox, oy = (w - 1 - sx, h - 1 - sy)

    opp_target = min(res, key=lambda t: (man((ox, oy), t), t[0], t[1]))

    best = (-10**18, 0, 0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue

            my_d_to_opp_target = man((nx, ny), opp_target)
            opp_d_to_opp_target = man((ox, oy), opp_target)

            # Interception pressure: prefer positions that make us closer to opponent's nearest target.
            # Secondary: also move toward our own nearest resource to avoid deadlocks.
            my_target = min(res, key=lambda t: (man((nx, ny), t), t[0], t[1]))
            my_d_to_my_target = man((nx, ny), my_target)

            sc = (opp_d_to_opp_target - my_d_to_opp_target) * 10 - my_d_to_my_target
            # Tiny deterministic tie-break
            sc = sc - (nx * 17 + ny * 31) * 1e-6

            if sc > best[0]:
                best = (sc, dx, dy)

    return [best[1], best[2]]