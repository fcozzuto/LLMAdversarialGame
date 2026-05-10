def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (sx, sy)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    my_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    best = (None, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        d_center = abs(nx - cx) + abs(ny - cy)
        d_self = abs(nx - sx) + abs(ny - sy)
        d_opp = abs(nx - ox) + abs(ny - oy)

        in_my = (nx, ny) in my_terr
        in_un = (nx, ny) in unclaimed
        in_op = (nx, ny) in op_terr

        # Heuristic: expand unclaimed, attack opponent territory when adjacent or close,
        # and keep momentum by preferring moves that don't worsen distance to center too much.
        adj_op = 0
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            tx, ty = nx + ax, ny + ay
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in op_terr:
                adj_op += 1

        score = 0.0
        if in_un:
            score += 220.0
        if in_my:
            score += 25.0
        if in_op:
            score += 160.0 + 30.0 * adj_op  # flipping on entry makes this attractive
        score += -2.2 * d_center
        score += 1.4 * d_opp if not in_op else 0.2 * d_opp  # when attacking, don't run away
        score += -0.05 * d_self

        # If already surrounded by my territory, slightly prefer stepping into boundary/unclaimed.
        if not in_un and not in_op:
            score -= 8.0 * (1 if (nx, ny) in my_terr else 0)

        if score > best[1]:
            best = ([dx, dy], score)

    if best[0] is None:
        return [0, 0]
    return best[0]