def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))

    obstacles = set()
    obs = observation.get("obstacles") or []
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_t.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if unclaimed:
        tx, ty = min(
            unclaimed,
            key=lambda p: (
                0 if ((abs(p[0]-ox) <= 1 and abs(p[1]-oy) <= 1 and (p[0], p[1]) in opp_t) or (p[0], p[1]) in opp_t) else 1,
                abs(p[0] - sx) + abs(p[1] - sy),
                p[0],
                p[1],
            ),
        )
    elif opp_t:
        tx, ty = min(opp_t, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    else:
        tx, ty = w // 2, h // 2

    best_score = None
    best_move = [0, 0]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d_to_target = abs(nx - tx) + abs(ny - ty)
            d_to_opp = abs(nx - ox) + abs(ny - oy)
            score = (-d_to_target, d_to_opp, nx, ny)
            if best_score is None or score < best_score:
                best_score = score
                best_move = [dx, dy]

    if ok(sx, sy):
        return best_move if best_move != [0, 0] else [0, 0]
    return best_move