def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) == 2:
            obs.add((p[0], p[1]))

    resources = observation.get("resources", []) or []
    if not resources:
        tx, ty = ox, oy
    else:
        tx, ty = None, None
        best = 10**9
        for r in resources:
            if r is None or len(r) != 2:
                continue
            rx, ry = r[0], r[1]
            d = abs(rx - sx) + abs(ry - sy)
            if d < best:
                best = d
                tx, ty = rx, ry
        if tx is None:
            tx, ty = ox, oy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        dist_t = abs(tx - nx) + abs(ty - ny) if tx is not None else 0
        dist_o = abs(ox - nx) + abs(oy - ny)
        score = (-dist_t) + 0.05 * dist_o
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]