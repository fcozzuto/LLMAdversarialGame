def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    blocked = {(p[0], p[1]) for p in obstacles}
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    # Target: be as close as possible relative to opponent; tie-break by raw distance.
    best_t = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in blocked:
            continue
        myd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (myd - od, myd)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)
    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    oppd_now = cheb(ox, oy, tx, ty)
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in blocked:
            continue
        myd = cheb(nx, ny, tx, ty)
        # Score: maximize our advantage; small penalty for being farther; contest opponent lightly.
        adv = oppd_now - myd
        dist_pen = -myd
        opp_close = -(cheb(nx, ny, ox, oy))
        score = (adv, dist_pen, opp_close, -(abs(nx - tx) + abs(ny - ty)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]