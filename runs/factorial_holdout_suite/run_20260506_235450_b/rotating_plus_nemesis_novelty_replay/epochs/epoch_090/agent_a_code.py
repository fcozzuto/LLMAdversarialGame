def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = (ox is not None and oy is not None)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid_moves.append((dx, dy))

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-10**9, 0, 0)
        for dx, dy in valid_moves:
            nx, ny = sx + dx, sy + dy
            sc = -(abs(nx - cx) + abs(ny - cy))
            if sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    # Pick a competitive target: prefer resources where we are closer; otherwise deny by maximizing (opp_dist - my_dist).
    best_t, best_val = None, -10**18
    for tx, ty in resources:
        my_d = abs(tx - sx) + abs(ty - sy)
        if opp_exists:
            opp_d = abs(tx - ox) + abs(ty - oy)
        else:
            opp_d = my_d + 1  # treat as if opponent is always farther
        lead = opp_d - my_d
        val = 100000 * (1 if my_d <= opp_d else 0) + 10 * lead - my_d
        if val > best_val:
            best_val = val
            best_t = (tx, ty)

    tx, ty = best_t
    best = (-10**18, 0, 0)
    for dx, dy in valid_moves:
        nx, ny = sx + dx, sy + dy
        my_d = abs(tx - nx) + abs(ty - ny)
        if opp_exists:
            opp_d = abs(tx - ox) + abs(ty - oy)  # opponent distance unchanged this turn
            lead = opp_d - my_d
            sc = 100000 * (1 if my_d <= opp_d else 0) + 10 * lead - my_d
        else:
            sc = -my_d
        if sc > best[0]:
            best = (sc, dx, dy)
    return [best[1], best[2]]