def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def eval_cell(x, y):
        if not resources:
            tx = gw - 1 if sx < gw // 2 else 0
            ty = gh - 1 if sy < gh // 2 else 0
            return -cheb(x, y, tx, ty)
        best_win = -10**18
        best_my = 10**18
        best_opp = 10**18
        for rx, ry in resources:
            d_me = cheb(x, y, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            if d_me < best_my:
                best_my, best_opp = d_me, d_op
            win = d_op - d_me
            if win > best_win:
                best_win = win
        return best_win * 1000 - best_my

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = eval_cell(nx, ny)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
        elif v == best_val:
            if abs(dx) + abs(dy) < abs(best_move[0]) + abs(best_move[1]):
                best_move = [dx, dy]

    if best_val == -10**18:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best_move