def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in obstacles_list:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick resource that we can reach sooner, but still favors positions where opponent is farther.
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not (0 <= rx < w and 0 <= ry < h) or (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Denier tends to contest; prefer being clearly closer, then shortest self distance.
        key = ((od - sd) * 10 - sd, -sd, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    if best is None:
        return [0, 0]

    _, tx, ty = best
    # Greedy step: move to reduce our chebyshev distance while keeping options safe.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (None, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_now = cheb(sx, sy, tx, ty)
        d_new = cheb(nx, ny, tx, ty)
        # Small secondary term to avoid stepping near obstacles less deterministically.
        # Favor larger increase in opponent distance (resource denial can be strong).
        opp_d_new = cheb(ox, oy, tx, ty)
        opp_factor = 0
        if opp_d_new == 0:
            opp_factor = -1000
        key = ((d_now - d_new) * 100 - d_new, -abs(nx - tx) - abs(ny - ty), -opp_factor, dx, dy)
        if best_move[0] is None or key > best_move[0]:
            best_move = (key, [dx, dy])

    if best_move[1] is None:
        return [0, 0]
    return best_move[1]