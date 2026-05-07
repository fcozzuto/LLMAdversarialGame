def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    res = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not res:
        return [0, 0]

    # Resource-denial aware: prioritize resources where we are closer than opponent, with stronger preference for immediate capture.
    best_cell = None
    best_key = None
    for rx, ry in res:
        self_d = manh(sx, sy, rx, ry)
        opp_d = manh(ox, oy, rx, ry)
        immediate = 1 if (self_d == 0) else 0
        # Key: maximize immediate, then maximize lead (opp_d - self_d), then prefer shorter self_d (earlier pickup).
        key = (immediate, opp_d - self_d, -self_d, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_cell = (rx, ry)

    rx, ry = best_cell
    # If we're already on a resource, stay.
    if sx == rx and sy == ry:
        return [0, 0]

    # Otherwise, choose the move that most reduces distance to chosen target; if tie, prefer moves that also increase our lead vs opponent.
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_d_next = manh(nx, ny, rx, ry)
        self_d_now = manh(sx, sy, rx, ry)
        dist_gain = self_d_now - self_d_next  # higher is better
        opp_to_target = manh(ox, oy, rx, ry)
        our_lead = (opp_to_target - self_d_next)
        mkey = (dist_gain, our_lead, -self_d_next, dx, dy)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]