def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', []) or []
    obstacles = observation.get('obstacles', []) or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    if not resources:
        return [0, 0]
    best_r = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        key = (adv, -ds, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        nds = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # Prefer smaller distance to target; if tie, prefer increasing relative advantage and moving toward center a bit.
        center_bias = - (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)) * 0.01
        score = (-nds, (nod - nds), center_bias, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]