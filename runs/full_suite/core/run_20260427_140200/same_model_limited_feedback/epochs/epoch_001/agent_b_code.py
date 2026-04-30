def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        best = None
        for rx, ry in resources:
            d_self = cheb(sx, sy, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; slightly prefer ones closer.
            key = (d_opp - d_self, -d_self, rx + ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        # No resources: move to maintain distance from opponent.
        tx, ty = ox, oy

    best_move = (None, None)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_t = cheb(nx, ny, tx, ty)
        d_o = cheb(nx, ny, ox, oy)
        # If targeting a resource, encourage moving onto it; also avoid becoming easy prey.
        if resources:
            score = (-d_t * 3.0) + (d_o * 0.2)
            # If we can tie for reaching target, favor moves that reduce opponent distance too.
            score += (-cheb(ox, oy, tx, ty) * 0.05)
        else:
            score = d_o * 1.0 - cheb(nx, ny, sx, sy) * 0.01
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move[1]):
            best_score = score
            best_move = (score, (dx, dy))

    if best_move[1] is None:
        return [0, 0]
    return [int(best_move[1][0]), int(best_move[1][1])]