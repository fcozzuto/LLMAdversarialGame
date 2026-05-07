def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        tx = gw - 2 if sx < gw // 2 else 1
        ty = gh - 2 if sy < gh // 2 else 1
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            tieb = (abs(nx - tx) + abs(ny - ty), dx, dy)
            cand = (d, tieb[0], 0)  # deterministic: dx,dy handled below
            if d < best[0] or (d == best[0] and (tieb[0], dx, dy) < (best[1], best[2], 0)):
                best = (d, tieb[0], dx)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny) and cheb(nx, ny, tx, ty) == best[0]:
                return [dx, dy]
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # choose resource that best fits "denier" style: maximize opponent advantage while closing ourselves
        move_val = -10**18
        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # primary: opponent farther than us; secondary: faster to reach; tertiary: avoid getting too close to opponent
            v = (opp_d - self_d) * 100 - self_d * 2 - manh(nx, ny, ox, oy) // 4
            if v > move_val:
                move_val = v
        # global tie-break: higher value, then lex order dx,dy to be deterministic
        if move_val > best_val or (move_val == best_val and (dx, dy) < best_move):
            best_val = move_val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]