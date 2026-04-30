def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    # Pick a target resource we are closest to (tie-break toward higher "steal advantage")
    best = None
    best_val = None
    for rx, ry in resources:
        ds = max(abs(rx - sx), abs(ry - sy))
        do = max(abs(rx - ox), abs(ry - oy))
        # Prefer resources we can reach sooner; slight bias toward reducing our distance overall
        val = (do - ds, -ds, rx, ry)
        if best_val is None or val > best_val:
            best_val = val
            best = (rx, ry)
    tx, ty = best

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Candidate move deltas
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Prefer direct progress; if blocked, choose best alternative by same objective
    cur_best = None
    cur_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds2 = max(abs(tx - nx), abs(ty - ny))
        # After moving, opponent objective (to contest) using greedy "sooner-than-opponent" bias
        do2 = max(abs(tx - ox), abs(ty - oy))
        val = ((do2 - ds2), -ds2, -((tx - nx) ** 2 + (ty - ny) ** 2), -dx, -dy)
        if cur_val is None or val > cur_val:
            cur_val = val
            cur_best = (dx, dy)
    if cur_best is None:
        return [0, 0]
    return [int(cur_best[0]), int(cur_best[1])]