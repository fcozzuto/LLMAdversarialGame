def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid_cell(x, y):
        return inside(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    res_cells = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid_cell(x, y):
                res_cells.append((x, y))
    if not res_cells:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid_cell(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    center = (w - 1) / 2.0, (h - 1) / 2.0

    def move_score(nx, ny):
        my_to_center = cheb(nx, ny, center[0], center[1])
        best_res = -10**9
        for rx, ry in res_cells:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd == 0:
                return 10**6
            # Prefer resources where we are closer than opponent; also prefer closer overall.
            s = (opd - myd) * 1000 - myd * 3 - my_to_center * 0.2
            best_res = s if s > best_res else best_res
        # If currently adjacent to opponent, avoid giving them immediate gain: slightly reduce moving into/near our line.
        opp_adj = cheb(nx, ny, ox, oy)
        if opp_adj <= 1:
            best_res -= 40
        # Mild obstacle avoidance: discourage stepping next to obstacles.
        ox_adj = 0
        for bx, by in obstacles:
            if cheb(nx, ny, bx, by) == 1:
                ox_adj += 1
        best_res -= ox_adj * 12
        return best_res

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid_cell(nx, ny):
            continue
        v = move_score(nx, ny)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
    return best_move