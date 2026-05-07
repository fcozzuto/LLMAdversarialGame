def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources_raw = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    resources = []
    for r in resources_raw:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    best_dx, best_dy = 0, 0
    if not resources:
        best = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            score = (abs(nx - ox) + abs(ny - oy))
            if score > best:
                best = score
                best_dx, best_dy = dx, dy
        return [best_dx, best_dy]

    def score_target(tx, ty):
        d_self = abs(tx - sx) + abs(ty - sy)
        d_opp = abs(tx - ox) + abs(ty - oy)
        # Prefer targets closer to us and farther from opponent
        return (d_opp - d_self) * 10 - (d_self)

    best_move_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # If we can collect now, prioritize heavily
        now_collect = 1 if (nx, ny) in set(resources) else 0

        # Choose which target we'd be aiming at after the move
        best_t = -10**18
        for tx, ty in resources:
            d_self2 = abs(tx - nx) + abs(ty - ny)
            d_opp2 = abs(tx - ox) + abs(ty - oy)
            s = (d_opp2 - d_self2) * 10 - d_self2
            if s > best_t:
                best_t = s

        # Small tie-break: avoid moving into positions that worsen approach to chosen target
        approach = -abs(nx - ox) - abs(ny - oy)

        move_score = now_collect * 1000 + best_t + approach
        if move_score > best_move_score:
            best_move_score = move_score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]