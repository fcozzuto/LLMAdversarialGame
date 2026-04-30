def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def sd(a, b, c, d): 
        dx, dy = a - c, b - d
        return dx * dx + dy * dy
    best_res = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = sd(sx, sy, rx, ry)
        do = sd(ox, oy, rx, ry)
        key = (do - ds, -ds, rx, ry)
        if best_key is None or key > best_key:
            best_key, best_res = key, (rx, ry)
    if best_res is None:
        # Fallback: move to maximize distance from opponent while staying valid
        best_move = (0, 0)
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            val = sd(nx, ny, ox, oy)
            if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val, best_move = val, (dx, dy)
        return [best_move[0], best_move[1]]
    tx, ty = best_res
    curr_self_d = sd(sx, sy, tx, ty)
    curr_opp_d = sd(ox, oy, tx, ty)
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ns_d = sd(nx, ny, tx, ty)
        no_d = sd(ox, oy, tx, ty)
        res_bonus = 0
        if (nx, ny) == (tx, ty):
            res_bonus = 1000000
        # Prefer approaching target; slight preference to keep opponent farther from it
        score = res_bonus + (curr_self_d - ns_d) + 0.01 * (no_d - curr_opp_d)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score, best_move = score, (dx, dy)
    return [best_move[0], best_move[1]]