def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    self_pos = observation.get('self_position', [0, 0])
    opp_pos = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', [])
    obstacles = observation.get('obstacles', [])
    sx, sy = self_pos
    ox, oy = opp_pos

    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs_set.add((int(p[0]), int(p[1])))

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return (dx*dx + dy*dy) ** 0.5

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
            valid.append((dx, dy, nx, ny))

    if not valid:
        return [0, 0]

    if not resources:
        best = None
        bestv = -1e18
        for dx, dy, nx, ny in valid:
            v = dist((nx, ny), (ox, oy))
            if v > bestv + 1e-9:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Choose a target resource that is relatively more accessible to us than to the opponent.
    best_target = None
    best_metric = -1e18
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        metric = do - ds
        if metric > best_metric + 1e-9:
            best_metric = metric
            best_target = (rx, ry)

    rx, ry = best_target
    # Evaluate moves: primary objective reduce our distance to target; secondary avoid getting too close to opponent.
    best_move = None
    best_score = -1e18
    for dx, dy, nx, ny in valid:
        d_me = dist((nx, ny), (rx, ry))
        d_op = dist((nx, ny), (ox, oy))
        score = -d_me + 0.15 * d_op
        # Small deterministic tie-break towards diagonal/forward-ish moves
        score += 1e-6 * (dx*dx + dy*dy) + 1e-7 * (dx + 2*dy)
        if score > best_score + 1e-12:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]