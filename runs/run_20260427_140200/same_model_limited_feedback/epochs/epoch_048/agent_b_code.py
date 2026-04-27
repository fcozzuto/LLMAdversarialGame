def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a target resource where we have maximum closeness advantage.
    best = None
    best_adv = -10**9
    my_pos = (sx, sy)
    opp_pos = (ox, oy)
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        dmy = dist(my_pos, (rx, ry))
        dop = dist(opp_pos, (rx, ry))
        adv = dop - dmy  # positive => we're closer
        # Tie-break toward closer overall
        if adv > best_adv or (adv == best_adv and dmy < dist(my_pos, (best[0], best[1])) if best else True):
            best_adv = adv
            best = (rx, ry)

    # If no resources, move toward farthest from opponent while avoiding obstacles.
    if best is None:
        best_move = (0, 0)
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            # maximize manhattan distance to opponent
            sc = dist((nx, ny), opp_pos)
            if sc > best_score:
                best_score = sc
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    tx, ty = best
    # Evaluate moves: reduce distance to target primarily, avoid obstacles, prefer higher advantage.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        dmy_next = dist((nx, ny), (tx, ty))
        # opponent's potential closeness to target proxy (assume they stay/move closer similarly by choosing their current best direction)
        # simple proxy: reduce our movement benefit by their current advantage and distance
        dop = dist(opp_pos, (tx, ty))
        adv_next = dop - dmy_next
        # also keep from giving opponent easy access by slightly maximizing distance from opponent
        sc = (adv_next * 1000) - (dmy_next * 10) + (dist((nx, ny), opp_pos) * 0.5)
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]