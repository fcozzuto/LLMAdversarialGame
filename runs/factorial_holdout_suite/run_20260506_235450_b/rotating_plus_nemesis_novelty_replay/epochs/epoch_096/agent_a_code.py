def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = ox is not None and oy is not None

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestd = 10**9
        for dx, dy in valid:
            d = abs((sx + dx) - tx) + abs((sy + dy) - ty)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    best_res = None
    best_key = None
    for tx, ty in resources:
        my_d = abs(tx - sx) + abs(ty - sy)
        if opp_exists:
            opp_d = abs(tx - ox) + abs(ty - oy)
            adv = opp_d - my_d
        else:
            adv = 10**6 - my_d
        # First prefer resources we can reach before opponent (adv>0). Then maximize adv.
        # Tie-break: smaller my distance.
        key = (adv <= 0, -adv, my_d, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (tx, ty)

    tx, ty = best_res
    # Move to reduce distance to target; if tied, prefer increasing advantage (deny opponent).
    best = None
    best_score = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        my_d2 = abs(tx - nx) + abs(ty - ny)
        if opp_exists:
            opp_d2 = abs(tx - ox) + abs(ty - oy)
            deny = opp_d2 - my_d2
        else:
            deny = 0
        score = (my_d2, -(deny), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]]