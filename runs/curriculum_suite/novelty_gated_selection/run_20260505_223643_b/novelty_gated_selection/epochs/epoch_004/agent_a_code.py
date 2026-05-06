def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = -10**18
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        move_best = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer

            # Strongly prefer being at least 1 step closer; then prefer closer target.
            lead = 200 * adv
            close_pen = 3.0 * ds

            # Contention shaping: if we are not closer, discourage.
            contention = 0.0
            if adv <= 0:
                contention = -80.0 * (1 - adv)  # harsher when worse

            score = lead - close_pen + contention

            # Slightly prefer targets that pull away from opponent direction (stabilize).
            opp_dir = cheb(nx, ny, ox, oy)
            score += 0.02 * opp_dir

            if score > move_best:
                move_best = score

        # Small tie-break: reduce distance to opponent if we can't gain lead (guard vs center_rush).
        if move_best == best:
            if cheb(nx, ny, ox, oy) < cheb(best_move[0], best_move[1], ox, oy):
                best_move = (dx, dy)

        if move_best > best:
            best = move_best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]