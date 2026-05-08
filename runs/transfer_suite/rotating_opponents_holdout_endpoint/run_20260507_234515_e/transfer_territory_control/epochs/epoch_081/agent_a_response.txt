def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        obstacles.add((int(p[0]), int(p[1])))

    self_terr = set()
    for p in (observation.get("self_territory") or []):
        self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in (observation.get("opponent_territory") or []):
        opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    # Deterministic "cutoff" target: unclaimed far from opponent but closer to us.
    best_target = None
    best_score = None
    max_eval = min(24, len(unclaimed))
    if unclaimed:
        for i in range(max_eval):
            x, y = int(unclaimed[i][0]), int(unclaimed[i][1])
            if (x, y) in obstacles:
                continue
            d_self = abs(x - sx) + abs(y - sy)
            d_opp = abs(x - ox) + abs(y - oy)
            # Prefer far-from-opp while not too far from us; slight preference toward our side.
            val = (2 * d_opp) - d_self + (x + y) * 1e-3
            if best_score is None or val > best_score:
                best_score = val
                best_target = (x, y)

    if best_target is None:
        # Fallback: head toward nearest border cell (often easier to claim safely).
        border = []
        for x in range(w):
            border.append((x, 0))
            border.append((x, h - 1))
        for y in range(1, h - 1):
            border.append((0, y))
            border.append((w - 1, y))
        border = [p for p in border if p not in obstacles]
        best_target = min(border, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))

    tx, ty = best_target
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_terr:
            flip_bonus = 20
        elif (nx, ny) in unclaimed:
            flip_bonus = 10
        else:
            flip_bonus = 0

        # Avoid stepping into cells the opponent is very close to; aim to reduce distance to target.
        d_t = max(0, abs(nx - tx) + abs(ny - ty))
        d_o = abs(nx - ox) + abs(ny - oy)
        val = flip_bonus + (d_o * 0.5) - d_t

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]