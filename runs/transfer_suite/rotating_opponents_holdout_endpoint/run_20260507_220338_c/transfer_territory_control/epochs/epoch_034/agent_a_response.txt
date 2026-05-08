def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles") or []):
        blocked.add((int(p[0]), int(p[1])))

    my_count = int(observation.get("self_territory_count", 0) or 0)
    opp_count = int(observation.get("opponent_territory_count", 0) or 0)
    behind = my_count <= opp_count

    unclaimed = [(int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or [])]
    opp_terr = [(int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or [])]
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]

    cx, cy = w // 2, h // 2
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = resources + (unclaimed if unclaimed else [])
    if behind and opp_terr:
        targets += opp_terr  # allow taking their control if flipping happens on entry

    if not targets:
        # deterministic fallback: head toward center
        dx = 0 if cx == sx else (1 if cx > sx else -1)
        dy = 0 if cy == sy else (1 if cy > sy else -1)
        return [dx, dy]

    best_move = (0, 0)
    best_score = 10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        # pick best target based on resulting position; add small penalties to avoid opponent crowding
        # when not behind, prefer unclaimed over opponent territory.
        local_best = 10**18
        for tx, ty in targets:
            d = abs(tx - nx) + abs(ty - ny)
            is_opp = (tx, ty) in set(opp_terr) if behind and opp_terr else False
            # bias: when behind, rush; otherwise expand to unclaimed and keep away from opponent
            center_bias = manh((nx, ny), (cx, cy))
            opp_bias = manh((nx, ny), (ox, oy))
            val = d + (0.08 * center_bias) + (0.05 * opp_bias if not behind else 0.02 * opp_bias)
            if not behind and is_opp:
                val += 6  # strongly avoid unnecessary contest when ahead
            local_best = val if val < local_best else local_best

        # also discourage stepping onto opponent territory too often when ahead
        step_pen = 0
        if (nx, ny) in set(opp_terr) and not behind:
            step_pen = 4
        score = local_best + step_pen

        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]