def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_targets(px, py):
        best = None
        for rx, ry in resources:
            d = md(px, py, rx, ry)
            if best is None or d < best[0] or (d == best[0] and (rx, ry) < best[1]):
                best = (d, (rx, ry))
        return best[1] if best else (w // 2, h // 2)

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        my_near = best_targets(sx, sy)
        opp_near = best_targets(ox, oy)
        my_d = md(sx, sy, my_near[0], my_near[1])
        opp_d = md(ox, oy, opp_near[0], opp_near[1])
        # If opponent is closer to their nearest, contest that area; else go for my nearest.
        tx, ty = opp_near if (my_near != opp_near and opp_d <= my_d + 1) else my_near

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    res_set = set((x, y) for x, y in resources)

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_to = md(nx, ny, tx, ty)
        opp_to = md(ox, oy, tx, ty)

        onto = 1 if (nx, ny) in res_set else 0
        # Contention pressure: prefer moves that reduce my distance and increase opponent distance.
        val = (onto * 1000) - my_to * 10 + (opp_to - my_to) * 2

        # If contesting, also try to move toward the opponent's nearest resource when close.
        if resources:
            opp_target = best_targets(ox, oy)
            if opp_target:
                val += (md(nx, ny, opp_target[0], opp_target[1]) <= my_to + 1) * 3

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]