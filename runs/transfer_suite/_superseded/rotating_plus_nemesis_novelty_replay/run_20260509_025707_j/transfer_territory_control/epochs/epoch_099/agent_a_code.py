def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((p[0], p[1]))

    myc = observation.get("self_territory_count", 0)
    opc = observation.get("opponent_territory_count", 0)
    behind = myc < opc

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obst:
            continue
        d_to_opp = abs(nx - ox) + abs(ny - oy)
        d_to_center = abs(nx - cx) + abs(ny - cy)
        adj_opp = (abs(nx - ox) <= 1 and abs(ny - oy) <= 1) and not (nx == ox and ny == oy)
        v = 0
        if behind:
            v = -d_to_opp * 10 - d_to_center + (3 if adj_opp else 0)
        else:
            v = -d_to_center * 10 + d_to_opp * 2 - (3 if adj_opp else 0)
        if best is None or v > bestv:
            best, bestv = (dx, dy), v

    if best is not None:
        return [best[0], best[1]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            return [dx, dy]
    return [0, 0]