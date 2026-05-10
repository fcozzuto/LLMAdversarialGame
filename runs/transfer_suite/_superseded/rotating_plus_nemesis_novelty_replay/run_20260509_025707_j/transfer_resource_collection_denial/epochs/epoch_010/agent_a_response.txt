def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Favor resources we are closer to; break ties toward faster/shorter self path
        key = (od - sd, -(sd), -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    # Candidate moves: all 9 (including stay), deterministic order
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Prefer moves that keep/expand lead on the chosen resource; if blocked, choose next-best
    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd2 = man(nx, ny, rx, ry)
        od2 = man(ox, oy, rx, ry)
        # Extra: if multiple resources, incorporate a quick peek for improved lead elsewhere
        peek_best = -10**9
        for r2 in resources:
            tx, ty = r2
            sd3 = man(nx, ny, tx, ty)
            od3 = man(ox, oy, tx, ty)
            v = od3 - sd3
            if v > peek_best:
                peek_best = v
        val = (od2 - sd2, peek_best, -sd2, -(nx + ny))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move