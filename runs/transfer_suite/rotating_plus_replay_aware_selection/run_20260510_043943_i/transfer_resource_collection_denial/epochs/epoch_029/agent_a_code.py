def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_raw)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return not inb(x, y) or (x, y) in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    best_tx, best_ty = resources[0]
    best_key = None
    for rx, ry in resources:
        d_self = man(sx, sy, rx, ry)
        d_opp = man(ox, oy, rx, ry)
        key = (d_self - d_opp, d_self, rx, ry)  # we prefer resources where we're relatively closer
        if best_key is None or key < best_key:
            best_key = key
            best_tx, best_ty = rx, ry

    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d_to_target = man(nx, ny, best_tx, best_ty)
        d_opp_next = man(nx, ny, ox, oy)
        d_opp_now = man(sx, sy, ox, oy)
        opp_push = 0
        if d_opp_next > d_opp_now:
            opp_push = -1  # slightly prefer moves that keep opponent farther
        val = (d_to_target, opp_push, -d_opp_next, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move