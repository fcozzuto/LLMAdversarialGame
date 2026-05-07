def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    if not res:
        tx, ty = w // 2, h // 2
    else:
        best = None
        best_key = None
        for tx, ty in res:
            sd = abs(tx - sx) + abs(ty - sy)
            od = abs(tx - ox) + abs(ty - oy)
            lead = od - sd  # positive => we're closer
            # Prefer resources we can reach first; otherwise reduce opponent reach
            key = (-1 if lead > 0 else 0, -lead, sd, od, tx, ty)
            if best_key is None or key < best_key:
                best_key = key
                best = (tx, ty)
        tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            continue
        nsd = abs(tx - nx) + abs(ty - ny)
        nod = abs(tx - ox) + abs(ty - oy)
        # discourage moves that allow quick opponent capture of the target by keeping us advancing
        opp_gate = abs(tx - ox) + abs(ty - oy)
        key = (nsd, -opp_gate, abs(ox - nx) + abs(oy - ny), tx - nx, ty - ny, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]