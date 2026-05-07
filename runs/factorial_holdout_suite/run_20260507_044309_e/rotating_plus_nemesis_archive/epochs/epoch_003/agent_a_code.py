def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    blocked = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                blocked.add((x, y))

    resources = observation.get("resources", []) or []
    res_pos = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int):
                if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                    res_pos.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if not res_pos:
        cx, cy = w // 2, h // 2
        best = None
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            v = -(abs(cx - nx) + abs(cy - ny))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    # Target selection: prefer resources where we are closer than the opponent.
    # Deterministic lexicographic tie-breaking.
    def tgt_key(t):
        x, y = t
        sd = abs(x - sx) + abs(y - sy)
        od = abs(x - ox) + abs(y - oy)
        return (sd - od, sd, x, y)

    target = min(res_pos, key=tgt_key)
    tx, ty = target

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        self_d = abs(tx - nx) + abs(ty - ny)
        opp_d = abs(tx - ox) + abs(ty - oy)

        # Move value: race the opponent (maximize opp margin) and reduce our distance.
        # Small preference to progress and discourage staying.
        progress = (abs(tx - sx) + abs(ty - sy)) - self_d
        stay_pen = 0.5 if (dx == 0 and dy == 0) else 0.0

        # Also lightly keep away from being "too aligned" with opponent by preferring steps that
        # increase our distance advantage to target compared to opponent's current distance.
        advantage = opp_d - self_d

        score = advantage * 10 + progress * 2 - stay_pen

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]