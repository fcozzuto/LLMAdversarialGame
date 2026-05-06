def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    def best_resource_from(posx, posy):
        if not resources:
            return None
        best = resources[0]
        best_tv = None
        for r in resources:
            tx, ty = r[0], r[1]
            d_me = abs(tx - posx) + abs(ty - posy)
            d_opp = abs(tx - ox) + abs(ty - oy)
            tv = (d_opp - d_me) * 1000 - d_me + (0.001 * d_opp)
            if best_tv is None or tv > best_tv or (tv == best_tv and (d_opp < (abs(best[0] - posx) + abs(best[1] - posy)))):
                best = r
                best_tv = tv
            elif tv == best_tv:
                if (tx, ty) < (best[0], best[1]):
                    best = r
                    best_tv = tv
        return best

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    target = best_resource_from(x, y)
    tx, ty = target[0], target[1]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        d_me = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(tx - ox) + abs(ty - oy)
        # Favor winning the approach; also prefer moving away from immediate opponent pressure a bit
        opp_pressure = max(0, 3 - (abs(nx - ox) + abs(ny - oy)))
        val = (d_opp - d_me) * 1000 - d_me - 5 * opp_pressure - 0.01 * (abs(nx - ox) + abs(ny - oy))
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    if best_val is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]