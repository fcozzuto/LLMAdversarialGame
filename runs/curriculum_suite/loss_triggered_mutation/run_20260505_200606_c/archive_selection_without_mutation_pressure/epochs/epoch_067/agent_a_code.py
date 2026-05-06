def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = {(p[0], p[1]) for p in obs_list if p is not None and len(p) >= 2}
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_t = None
    best_score = -10**9
    best_our = 10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d_our = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        score = d_opp - d_our
        if score > best_score or (score == best_score and d_our < best_our):
            best_score = score
            best_our = d_our
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    best_move = [0, 0]
    best_dist = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        if d < best_dist or (d == best_dist and (dx, dy) != (0, 0) and (best_move == [0, 0])):
            best_dist = d
            best_move = [dx, dy]

    if best_dist == 10**9:
        return [0, 0]
    return best_move