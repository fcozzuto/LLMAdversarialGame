def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None
    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            key = -(cheb(nx, ny, tx, ty))
            if best_key is None or key > best_key:
                best_key = key
                best = [dx, dy]
        if best is None:
            return [0, 0]
        return best
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        best_adv = None
        best_d = None
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            adv = d_opp - d_self
            if best_adv is None or adv > best_adv or (adv == best_adv and d_self < best_d):
                best_adv = adv
                best_d = d_self
        # prioritize capturing/approaching a favorable resource; tie-break deterministically by direction order
        key = (best_adv, -best_d, -cheb(nx, ny, ox, oy), -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best