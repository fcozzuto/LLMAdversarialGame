def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose target with stronger "win first"; otherwise choose one that minimizes opponent advantage.
    best = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        if myd <= opd:
            key = (0, myd, opd, rx, ry)
        else:
            key = (1, opd - myd, myd, -opd, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    best_move = [0, 0]
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Move scoring: get closer to target; if opponent also races, prioritize blocking by increasing opponent's distance.
        mydn = man(nx, ny, tx, ty)
        opdn = man(ox, oy, tx, ty)
        # If we don't beat opponent on the target, also consider reducing opponent's progress toward it.
        # (Use current opponent position distance; deterministic and cheap.)
        adv = mydn - opdn
        opp_focus = -man(nx, ny, ox, oy)  # prefer moves that keep spacing from opponent slightly
        key = (mydn > man(sx, sy, tx, ty),  # prefer non-regressive
               0 if mydn <= man(ox, oy, tx, ty) else 1,
               adv,
               mydn,
               -opdn,
               opp_focus,
               rx_dum if False else 0)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    # Fallback: any valid move that doesn't step into obstacles and roughly heads toward target.
    if best_key is None:
        mx = 0 if tx == sx else (1 if tx > sx else -1)
        my = 0 if ty == sy else (1 if ty > sy else -1)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny) and (dx == mx or dx == 0 or dy == my or dy == 0):
                return [dx, dy]
        return [0, 0]

    return best_move