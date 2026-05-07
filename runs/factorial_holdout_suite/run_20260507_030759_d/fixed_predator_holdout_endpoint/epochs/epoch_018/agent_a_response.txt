def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))

    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in valid:
            d = max(abs(nx - tx), abs(ny - ty))
            cand = (d, abs(ox - nx) - abs(ox - sx), abs(dx) + abs(dy), dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[3], best[4]]

    res_set = {(r[0], r[1]) for r in resources}

    def target_value(rx, ry):
        self_d = abs(rx - sx) + abs(ry - sy)
        opp_d = abs(rx - ox) + abs(ry - oy)
        # Prefer resources we are closer to; strongly reward immediate pickup.
        on_pick = 1 if (sx, sy) == (rx, ry) else 0
        pickup = 100000 if (rx, ry) in res_set else 0
        return (-on_pick, pickup, opp_d - self_d, -self_d)

    tx, ty = None, None
    best_tv = None
    for r in resources:
        rx, ry = r[0], r[1]
        tv = target_value(rx, ry)
        if best_tv is None or tv < best_tv:
            best_tv = tv
            tx, ty = rx, ry

    def step_toward(nx, ny):
        return (abs(tx - nx) + abs(ty - ny), max(abs(tx - nx), abs(ty - ny)))

    best = None
    for dx, dy, nx, ny in valid:
        on_resource = 1 if (nx, ny) in res_set else 0
        d_self = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(tx - ox) + abs(ty - oy)
        # If we land on a resource, dominate; otherwise move to reduce our distance,
        # while mildly increasing the chance opponent can't easily take it next.
        cand = (
            -on_resource,
            d_self,
            d_opp - (abs(tx - nx) + abs(ty - ny)),
            abs(dx) + abs(dy),
            dx,
            dy,
        )
        if best is None or cand < best:
            best = cand

    return [best[4], best[5]]