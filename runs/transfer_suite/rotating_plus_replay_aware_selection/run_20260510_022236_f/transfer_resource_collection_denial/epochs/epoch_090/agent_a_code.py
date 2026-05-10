def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    tr = int(observation.get("turns_remaining", 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid = []
    for x, y in resources:
        x, y = int(x), int(y)
        if inb(x, y) and (x, y) not in obs:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    best = None
    for rx, ry in valid:
        ds = cheb_dist(sx, sy, rx, ry)
        do = cheb_dist(ox, oy, rx, ry)
        # Win-tie heuristic: maximize lead to resource; then minimize our time; then prefer mid-grid y to avoid getting stuck.
        lead = do - ds
        time_term = ds
        y_pref = -abs((ry - (h - 1) / 2.0))
        score = (lead, -time_term, y_pref)
        if best is None or score > best[0]:
            best = (score, rx, ry, ds, do)
    _, tx, ty, ds, do = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    def eval_move(mx, my):
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obs:
            return None
        n_d = cheb_dist(nx, ny, tx, ty)
        n_o = cheb_dist(ox, oy, tx, ty)
        # Prefer moves that keep/extend our lead; also reduce our distance.
        return ( (n_o - n_d), -n_d, -(abs(ty - ny)) )

    candidates = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0), (0, -dy), (-dx, 0), (-dx, -dy)]
    best_eval = None
    best_move = (0, 0)
    for mx, my in candidates:
        r = eval_move(mx, my)
        if r is None:
            continue
        if best_eval is None or r > best_eval:
            best_eval = r
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]