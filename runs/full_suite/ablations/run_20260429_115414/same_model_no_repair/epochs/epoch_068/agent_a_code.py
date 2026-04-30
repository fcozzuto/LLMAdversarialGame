def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def passable(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid_moves_from(x, y):
        out = []
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if passable(nx, ny):
                out.append((dx, dy, nx, ny))
        return out

    if resources:
        best_r = None
        best_d = 10**9
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if d < best_d:
                best_d = d
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = w // 2, h // 2

    moves = valid_moves_from(sx, sy)
    if not moves:
        return [0, 0]

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy, nx, ny in moves:
        dist_to_target = cheb(nx, ny, tx, ty)
        dist_to_opp = cheb(nx, ny, ox, oy)
        # Primary: get closer to target; Secondary: keep away from opponent
        score = -dist_to_target * 10 + dist_to_opp
        # Small nudge to reduce oscillation: prefer staying off exact backtrack
        if dx == 0 and dy == 0:
            score -= 0.5
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]