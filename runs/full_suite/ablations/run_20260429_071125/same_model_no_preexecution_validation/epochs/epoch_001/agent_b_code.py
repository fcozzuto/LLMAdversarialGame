def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        dx = 0
        dy = 0
        return [dx, dy]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    # Pick resource to maximize relative advantage (lower myd-opd is better).
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = dist((sx, sy), (rx, ry))
        opd = dist((ox, oy), (rx, ry))
        key = myd - opd  # prefer being closer than opponent
        # tie-break: prefer closer absolute distance
        if best_key is None or key < best_key or (key == best_key and myd < best[0]):
            best = (myd, rx, ry)
            best_key = key
    _, tx, ty = best

    # Candidate moves (including stay)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            return False
        if (nx, ny) in obstacles:
            return False
        return True

    # Choose move that minimizes distance to target, but avoid moves that let opponent get closer.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = dist((nx, ny), (tx, ty))
        opd = dist((ox, oy), (tx, ty))
        # relative: smaller is better, add penalty if we move away from target
        rel = myd - opd
        move_pen = myd  # keep progressing
        opp_close = 0
        # If we are moving into opponent vicinity of target, discourage
        if dist((nx, ny), (ox, oy)) <= 1:
            opp_close = 2
        score = (rel, move_pen + opp_close)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move