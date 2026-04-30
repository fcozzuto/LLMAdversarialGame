def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

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

    if not resources:
        # Deterministic: drift toward center a bit to reduce worst-case
        cx, cy = w // 2, h // 2
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        # else try simple alternatives
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                nx, ny = sx + ddx, sy + ddy
                if valid(nx, ny):
                    return [ddx, ddy]
        return [0, 0]

    best = None
    best_key = None
    # Prefer resources we can reach no later than opponent; break ties by our distance then target position.
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # primary: contest (myd <= opd), then lead by margin, then smaller myd, then smaller x+y to stabilize
        contest = 1 if myd <= opd else 0
        margin = opd - myd
        key = (0 if contest else 1, -margin, myd, rx + ry, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    raw_dx = 0 if sx == tx else (1 if sx < tx else -1)
    raw_dy = 0 if sy == ty else (1 if sy < ty else -1)

    candidates = []
    # candidate deltas with preference toward target (including diagonals)
    for dx in (raw_dx, raw_dx - 1, raw_dx + 1):
        if dx < -1 or dx > 1:
            continue
        for dy in (raw_dy, raw_dy - 1, raw_dy + 1):
            if dy < -1 or dy > 1:
                continue
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                # score by resulting distance to target; tie by dx,dy order deterministically
                candidates.append((cheb(nx, ny, tx, ty), dx, dy))
    if candidates:
        candidates.sort()
        return [int(candidates[0][1]), int(candidates[0][2])]

    # If blocked, deterministic search among all valid moves for minimal distance to target
    all_dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_dist = None
    for dx, dy in all_dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        key = (d, abs(dx), abs(dy), dx, dy)
        if best_move is None or key < best_move:
            best_move = key
            best_dist = d
            best_dx, best_dy = dx, dy
    if best_move is None:
        return [0, 0]
    return [int(best_dx), int(best_dy)]