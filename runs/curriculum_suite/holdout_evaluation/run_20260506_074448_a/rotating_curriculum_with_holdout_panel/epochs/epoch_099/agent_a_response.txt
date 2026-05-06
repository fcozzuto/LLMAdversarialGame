def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles") or [])
    resources = [tuple(r) for r in (observation.get("resources") or [])]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_move = [0, 0]
    # If no resources, drift toward center while keeping distance from opponent.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)) - 0.12 * ((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy))
            if best is None or sc > best or (sc == best and (dx, dy) < tuple(best_move)):
                best = sc
                best_move = [dx, dy]
        return best_move

    # Resource-advantage interception: prefer targets we can reach sooner than opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        best_adv = None
        best_d = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive means we're closer
            if best_adv is None or adv > best_adv or (adv == best_adv and (best_d is None or sd < best_d)):
                best_adv = adv
                best_d = sd
        # Secondary terms: avoid getting too close to opponent (reduces direct sweep fights) while still moving purposefully.
        opp_close = man(nx, ny, ox, oy)
        sc = (best_adv * 3.0) - (best_d if best_d is not None else 0) + 0.08 * opp_close
        if best is None or sc > best or (sc == best and (dx, dy) < tuple(best_move)):
            best = sc
            best_move = [dx, dy]
    return best_move