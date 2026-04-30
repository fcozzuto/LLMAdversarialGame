def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = set((p[0], p[1]) for p in obstacles)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cx = (w - 1) // 2
    cy = (h - 1) // 2
    best = [0, 0]
    best_score = None

    # If no resources, drift to center while staying safe and separating from opponent
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            score = cheb(nx, ny, cx, cy)
            sep = cheb(nx, ny, ox, oy)
            if best_score is None or score < best_score or (score == best_score and sep > cheb(sx, sy, ox, oy)):
                best_score = score
                best = [dx, dy]
        return best if best_score is not None else [0, 0]

    # Otherwise, greedily move toward nearest resource; break ties by maximizing distance to opponent
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        best_r = None
        for rx, ry in resources:
            dist = cheb(nx, ny, rx, ry)
            if best_r is None or dist < best_r:
                best_r = dist
        if best_r is None:
            continue
        opp_sep = cheb(nx, ny, ox, oy)
        score = (best_r, -opp_sep, dx == 0 and dy == 0)
        if best_score is None or score < best_score:
            best_score = score
            best = [dx, dy]

    return best if best_score is not None else [0, 0]