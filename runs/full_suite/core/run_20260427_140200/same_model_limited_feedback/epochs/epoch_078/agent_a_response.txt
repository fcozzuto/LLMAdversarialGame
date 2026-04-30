def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = set((x, y) for x, y in obstacles)

    def sqdist(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if not resources:
        tx, ty = (W - 1) / 2.0, (H - 1) / 2.0
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= W or ny >= H or (nx, ny) in obs_set:
                continue
            v = sqdist(nx, ny, tx, ty)
            if bestv is None or v < bestv:
                bestv = v
                best = [dx, dy]
        return best if best is not None else [0, 0]

    best_target = None
    best_key = None
    for rx, ry in resources:
        ds = sqdist(sx, sy, rx, ry)
        do = sqdist(ox, oy, rx, ry)
        key = (ds - do, ds)  # I prefer resources I can reach sooner
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= W or ny >= H or (nx, ny) in obs_set:
            continue
        my_d = sqdist(nx, ny, tx, ty)
        opp_d = sqdist(nx, ny, ox, oy)
        # Prefer getting closer to target; also prefer being farther from opponent to avoid contest
        score = (my_d, -opp_d, dx * 2 + dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move