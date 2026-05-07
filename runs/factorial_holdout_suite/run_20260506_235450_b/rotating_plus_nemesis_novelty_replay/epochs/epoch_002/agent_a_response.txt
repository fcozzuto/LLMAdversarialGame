def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = min(corners, key=lambda p: (abs(p[0] - ox) + abs(p[1] - oy), p[0], p[1]))
        if (sx, sy) == (tx, ty):
            tx, ty = max(corners, key=lambda p: (abs(p[0] - ox) + abs(p[1] - oy), -p[0], -p[1]))
        best_move = [0, 0]
        best_key = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            key = (dist2(nx, ny, tx, ty), abs(nx - ox) + abs(ny - oy), nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]
        return best_move

    best_res = None
    best_sd = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dist2(sx, sy, rx, ry)
        od = dist2(ox, oy, rx, ry)
        # If opponent is much closer, penalize; otherwise prefer nearer resources and deterministic tie-break.
        val = (sd - (od // 3), sd, od, rx, ry)
        if best_res is None or val < best_res[0]:
            best_res = (val, rx, ry)
            best_sd = sd

    _, tx, ty = best_res
    best_move = [0, 0]
    best_key = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = dist2(nx, ny, tx, ty)
        opd = dist2(nx, ny, ox, oy)
        # Prefer stepping that advances toward target; slight preference for moving away from opponent to avoid steals.
        key = (myd, -opd, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move