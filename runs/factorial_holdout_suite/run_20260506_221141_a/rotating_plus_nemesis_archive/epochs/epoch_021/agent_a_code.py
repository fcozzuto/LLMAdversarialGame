def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if not resources:
        return [0, 0]

    if (sx, sy) in set(map(tuple, resources)):
        # stay if we are on a resource
        return [0, 0]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Target resources where the opponent is currently closer (to contest/deny).
    best = None
    best_key = None
    for rx, ry in resources:
        self_d = manh(sx, sy, rx, ry)
        opp_d = manh(ox, oy, rx, ry)
        # Prefer large "we are behind" and also those closer to us overall.
        key = (self_d - opp_d, -self_d, -(rx * 8 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Choose move that most reduces our disadvantage relative to the opponent for this target.
    best_move = [0, 0]
    best_mkey = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd_new = manh(nx, ny, tx, ty)
        od_new = manh(ox, oy, tx, ty)
        # Minimize (self advantage: sd_new - od_new). Tie-break on smaller sd_new and prefer dx/dy toward target.
        mkey = (sd_new - od_new, sd_new, abs(nx - tx) + abs(ny - ty), -dx, -dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = [dx, dy]

    return best_move