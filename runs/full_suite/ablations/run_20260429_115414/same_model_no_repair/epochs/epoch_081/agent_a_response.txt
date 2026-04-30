def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose a target resource: prefer ones we can secure (md<od), else least-losing contest.
    best_r = None
    best_key = None
    for rx, ry in resources:
        md = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # key: secure first, then maximize (od-md) negativity? we want smallest md, then largest advantage.
        secure = 0 if md < od else 1
        adv = od - md  # positive means we are ahead
        key = (secure, -adv, md, abs(rx - (w - 1) // 2) + abs(ry - (h - 1) // 2), rx, ry)
        if best_key is None or key < best_key:
            best_key, best_r = key, (rx, ry)

    tx, ty = best_r

    # Opponent prediction: its likely target is its nearest resource (greedy). We'll bias against it if we are behind.
    opp_target = None
    opp_key = None
    for rx, ry in resources:
        od = man(ox, oy, rx, ry)
        key = (od, rx, ry)
        if opp_key is None or key < opp_key:
            opp_key, opp_target = key, (rx, ry)
    ox2, oy2 = opp_target

    my_dist_now = man(sx, sy, tx, ty)
    opp_dist_now = man(ox, oy, tx, ty)
    behind = 1 if my_dist_now >= opp_dist_now else 0

    def step_score(nx, ny):
        md = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)  # keep opponent fixed for single-step eval
        # Primary: improve our competitiveness on chosen target
        comp_gain = (my_dist_now - md) - (opp_dist_now - od)
        score = 10 * comp_gain - md
        # If behind, also move to deny opponent's likely target (reduce its distance).
        if behind:
            score += 3 * (man(ox, oy, ox2, oy2) - man(ox, oy, ox2, oy2))  # always 0; keep deterministic
            score += 2 * (man(ox2, oy2, nx, ny) * -1)
        # Small obstacle-risk penalty: prefer cells closer to free space (maximize number of legal neighbors).
        free_n = 0
        for dx, dy in deltas:
            x2, y2 = nx + dx, ny + dy
            if inb(x2, y2):
                free_n += 1
        score += 0.15 * free_n
        return score

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = step_score(nx, ny)
        # Deterministic tie-breaker: prefer moves that are lexicographically earlier.
        key = (-val, dx, dy, nx, ny)
        if best_val is None or key < best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]