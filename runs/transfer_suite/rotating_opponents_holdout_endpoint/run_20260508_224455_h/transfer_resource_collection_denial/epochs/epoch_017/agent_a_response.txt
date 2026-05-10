def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    if (sx, sy) in obstacles or not resources:
        return [0, 0]

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        key = (od - sd, -sd, -((rx + ry) & 7), -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_d = man(sx, sy, tx, ty)

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = man(nx, ny, tx, ty)
        opp_nd = man(nx, ny, ox, oy)
        # Prefer strict improvement; tie-break with staying closer to target and away from opponent.
        improve = 1 if nd < cur_d else 0
        score = (improve, -nd, -opp_nd, -dx, -dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    if best_score is not None:
        return best_move

    # Fallback: allow staying still if all forward cells are blocked.
    return [0, 0]