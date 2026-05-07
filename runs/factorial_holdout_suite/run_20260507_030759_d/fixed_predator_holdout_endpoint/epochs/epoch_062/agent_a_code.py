def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set((int(p[0]), int(p[1])) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def pick_target():
        if not resources:
            return None
        best = None
        best_key = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            x, y = int(r[0]), int(r[1])
            sd = md(sx, sy, x, y)
            od = md(ox, oy, x, y)
            # Prefer resources we can reach sooner; also value "denial" (od - sd)
            key = (od - sd, -sd, -x, -y)
            if best_key is None or key > best_key:
                best_key = key
                best = (x, y)
        return best

    target = pick_target()
    if target is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                return [dx, dy]
        return [0, 0]

    tx, ty = target
    # Evaluate candidate moves by resulting distance to target plus denial pressure
    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        self_d = md(nx, ny, tx, ty)
        opp_d = md(ox, oy, tx, ty)
        # Encourage faster collection; also discourage giving opponent a closer path
        score = (opp_d - self_d, -self_d, -abs(nx - ox) - abs(ny - oy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move