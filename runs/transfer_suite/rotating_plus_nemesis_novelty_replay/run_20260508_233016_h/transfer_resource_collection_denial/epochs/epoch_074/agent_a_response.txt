def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Pick best resource deterministically with a secure/deny heuristic
    best = None
    best_key = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        if my_d < op_d:
            key = (0, my_d, op_d, rx, ry)
        else:
            key = (1, -(op_d - my_d), my_d, op_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    secure = cheb(sx, sy, tx, ty) < cheb(ox, oy, tx, ty)

    # Greedy step with obstacle avoidance; if deny, also try to increase opponent distance
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_next = cheb(nx, ny, tx, ty)
        if secure:
            opp_next = cheb(nx, ny, ox, oy)
            score = (my_next, opp_next, dx, dy)
        else:
            opp_next = cheb(ox, oy, tx, ty)
            score = (my_next, -(opp_next - cheb(nx, ny, tx, ty)), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]