def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            occ.add((p[0], p[1]))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in occ:
                continue
            d = abs(rx - sx) + abs(ry - sy)
            key = (d, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        if best is not None:
            tx, ty = best[1]
        else:
            tx, ty = w // 2, h // 2
    else:
        tx, ty = w // 2, h // 2
    best_key = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in occ:
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        key = (dist, nx, ny, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move