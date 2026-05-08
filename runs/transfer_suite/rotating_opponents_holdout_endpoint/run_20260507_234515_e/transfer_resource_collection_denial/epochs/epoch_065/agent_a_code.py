def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    dirs = (-1, 0, 1)
    moves = []
    for dx in dirs:
        for dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def nearest_dist(pos):
        best = 10**9
        for rx, ry in res:
            d = abs(pos[0] - rx) + abs(pos[1] - ry)
            if d < best:
                best = d
        return best

    self_to_nearest = nearest_dist((sx, sy))
    opp_to_nearest = nearest_dist((ox, oy))
    turns_remaining = observation.get("turns_remaining", 0)
    try:
        tr = int(turns_remaining)
    except:
        tr = 0
    urgency = 1.0 + max(0, 64 - tr) / 64.0

    best_move = (0, 0)
    best_val = -10**18

    # Choose move that maximizes (how much we beat opponent to a good resource),
    # while avoiding moves that worsen our nearest distance.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        cur_best = -10**18
        for rx, ry in res:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            # Primary: win margin; Secondary: closeness to resource; Tertiary: keep ahead near-term.
            margin = od - sd
            closeness = -sd
            near_term = -(sd - self_to_nearest)
            val = margin * 1000 + closeness * 3 + near_term * 2 * urgency
            if val > cur_best:
                cur_best = val
        # If opponent is much closer to nearest resource, prioritize reducing our nearest dist.
        nd = nearest_dist((nx, ny))
        penalty = 0
        if nd > self_to_nearest and opp_to_nearest < self_to_nearest:
            penalty = (nd - self_to_nearest) * (20 + 5 * urgency)
        total = cur_best - penalty
        if total > best_val:
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]