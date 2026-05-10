def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    obs_raw = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_raw)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)
    target = resources[0]
    best_t = None
    for r in resources:
        tx, ty = r[0], r[1]
        d = man(sx, sy, tx, ty)
        if best_t is None or d < best_t:
            best_t = d
            target = (tx, ty)
    tx, ty = target
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_t = man(nx, ny, tx, ty)
        d_to_o = man(nx, ny, ox, oy)
        opp_d = man(ox, oy, tx, ty)
        score = -d_to_t + (0.001 * d_to_o) + (0.1 if d_to_t <= opp_d else 0.0)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    if best_score is None:
        return [0, 0]
    return [best_move[0], best_move[1]]