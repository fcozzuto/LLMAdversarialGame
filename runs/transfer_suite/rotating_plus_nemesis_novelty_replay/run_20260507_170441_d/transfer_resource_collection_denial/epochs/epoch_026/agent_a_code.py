def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set((p[0], p[1]) for p in obstacles)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_val = None
    best_move = [0, 0]

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Evaluate move by targeting resources we can beat the opponent on "arrival time"
        chosen = None
        for rx, ry in resources:
            selfd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            margin = oppd - selfd
            # Prefer winning captures (margin>=2), then larger margin, then shorter self distance, then smaller opp distance
            val = (0 if margin >= 2 else 1, -margin, selfd, oppd)
            if chosen is None or val < chosen:
                chosen = val
        if chosen is None:
            continue
        # Overall move score: first category (win vs race), then best target margin, then minimize self distance
        # Tie-break deterministically by (dx,dy)
        move_val = (chosen[0], chosen[1], chosen[2], chosen[3], dx, dy)
        if best_val is None or move_val < best_val:
            best_val = move_val
            best_move = [dx, dy]

    if best_val is None:
        return [0, 0]
    return best_move