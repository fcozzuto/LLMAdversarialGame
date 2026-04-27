def choose_move(observation):
    W = observation.get('grid_width', 8)
    H = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set((x, y) for x, y in observation.get('obstacles', []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a contest target: resource where we are closest relative to opponent
    best_r = None
    best_rel = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        rel = ds - do
        if best_rel is None or rel < best_rel or (rel == best_rel and ds < cheb(sx, sy, best_r[0], best_r[1])):
            best_rel = rel
            best_r = (rx, ry)

    if best_r is None:
        # No resources: stay or drift away from opponent deterministically
        tx, ty = sx, sy
    else:
        tx, ty = best_r

    # Evaluate candidate moves
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= W or ny >= H:
            continue
        if (nx, ny) in obstacles:
            continue

        ds_t = cheb(nx, ny, tx, ty)
        ds_c = cheb(nx, ny, sx, sy)
        do_n = cheb(nx, ny, ox, oy)

        # Make meaningful change: prioritize denying opponent by moving to a target they are close to,
        # while also keeping distance from them to avoid swaps/collisions.
        # Score: lower distance to target is better; penalize being too close to opponent.
        # Also add slight tie-break toward moving when progress is possible.
        score = (-ds_t * 10) + (do_n * 0.6) + (-ds_c * 0.05)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]