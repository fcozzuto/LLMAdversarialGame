def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    # Choose a target resource that we can reach at least as fast as the opponent.
    best_r = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer: smallest own distance, then biggest advantage (od - sd), then deterministic ordering.
        key = (sd, -(od - sd), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    # Consider legal moves (including stay), avoid obstacles and bounds.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Primary: reduce distance to target.
        nd = cheb(nx, ny, rx, ry)
        cd = cheb(sx, sy, rx, ry)
        # Secondary: keep away from opponent while advancing.
        oppd = cheb(nx, ny, ox, oy)
        cur_oppd = cheb(sx, sy, ox, oy)
        # If moving away from target would be worse, avoid it; otherwise prioritize safety/spacing.
        # Deterministic scoring: lower is better.
        score = (nd, -(oppd), -((cd - nd)), abs(nx - rx) + abs(ny - ry), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]