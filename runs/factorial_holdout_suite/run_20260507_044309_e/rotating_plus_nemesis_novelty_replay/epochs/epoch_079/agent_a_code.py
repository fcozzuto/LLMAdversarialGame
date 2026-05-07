def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def pick_opp_next(ax, ay, tx, ty):
        best = (10**9, ax, ay)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = ax + dx, ay + dy
                if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                    continue
                d = cheb(nx, ny, tx, ty)
                if d < best[0] or (d == best[0] and (nx < best[1] or (nx == best[1] and ny < best[2]))):
                    best = (d, nx, ny)
        return best[1], best[2]

    if not res:
        return [0, 0]

    self_moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                self_moves.append((dx, dy, nx, ny))
    if not self_moves:
        return [0, 0]

    best_move = (0, 0, -10**9)
    for dx, dy, nsx, nsy in self_moves:
        best_for_move = -10**9
        for rx, ry in res:
            if (rx, ry) in obstacles:
                continue
            d_self = cheb(nsx, nsy, rx, ry)
            ox2, oy2 = pick_opp_next(ox, oy, rx, ry)
            d_opp = cheb(ox2, oy2, rx, ry)
            # Strong preference for resources we can reach strictly earlier; then for closer.
            lead = d_opp - d_self
            row_bias = 0
            if ry == nsy:
                row_bias = 0.1
            if rx == nsx:
                row_bias += 0.1
            # If tie or behind, heavily penalize (resource_denier).
            score = (lead * 100.0) - d_self + row_bias
            if lead <= 0:
                score -= (50.0 + 10.0 * cheb(sx, sy, rx, ry))
            if score > best_for_move:
                best_for_move = score
        if best_for_move > best_move[2]:
            best_move = (dx, dy, best_for_move)

    return [int(best_move[0]), int(best_move[1])]