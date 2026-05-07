def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    best_target = None
    best_key = None
    for x, y in resources:
        sd = abs(x - sx) + abs(y - sy)
        od = abs(x - ox) + abs(y - oy)
        race = od - sd  # we are closer if positive
        key = (race, -sd, -od, x, y)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (x, y)

    tx, ty = best_target

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer improving towards target and deny opponent by being closer to the chosen resource.
        my_d = abs(tx - nx) + abs(ty - ny)
        opp_d = abs(tx - ox) + abs(ty - oy)
        # Denial pressure: for other resources, slightly prefer cells where opponent is farther.
        denial = 0
        for rx, ry in resources:
            if rx == tx and ry == ty:
                continue
            if abs(rx - nx) + abs(ry - ny) == 0:
                continue
            denial += (abs(rx - ox) + abs(ry - oy)) - (abs(rx - nx) + abs(ry - ny))
        score = (-(my_d), denial, -(abs(ox - nx) + abs(oy - ny)), -abs(dx) - abs(dy), nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]