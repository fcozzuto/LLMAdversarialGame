def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    target = None
    if resources:
        bestd = 10**9
        for rx, ry in resources:
            d = abs(rx - sx) + abs(ry - sy)
            if d < bestd:
                bestd = d
                target = (rx, ry)
    if not target:
        return [0, 0]
    tx, ty = target
    moves = [(0,0), (-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]
    best = None
    best_score = 10**18
    resset = set(tuple(p) for p in resources)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        odist = abs(ox - nx) + abs(oy - ny)
        sc = dist * 10 - odist
        if (nx, ny) in resset:
            sc -= 50
        if sc < best_score:
            best_score = sc
            best = (dx, dy)
    return list(best) if best is not None else [0, 0]