def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs_set = set(map(tuple, obstacles))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Predict opponent next step greedily towards best currently deniable resource
    def opp_best_resource():
        best = None
        bestv = -10**9
        for r in resources:
            sd = man(r, (ox, oy))
            # opponent_denier: choose close resource; tie-break by lexicographic
            v = -sd * 10 - (r[0] * 0 + r[1] * 0)  # deterministic base
            if v > bestv or (v == bestv and r < best):
                bestv = v
                best = r
        return best

    target_opp = opp_best_resource()
    opp_dir = (0, 0)
    if target_opp:
        tx, ty = target_opp
        opp_dir = (0 if tx == ox else (1 if tx > ox else -1), 0 if ty == oy else (1 if ty > oy else -1))

    def blocked(x, y):
        return (x, y) in obs_set

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        # If we step onto a resource, huge score
        on_res = 1 if (nx, ny) in set(map(tuple, resources)) else 0

        # Compute best "lead" after move against any resource
        self_pos = (nx, ny)
        self_best = -10**9
        deniable_line_pen = 0

        for r in resources:
            sd = man(r, self_pos)
            od = man(r, (ox + opp_dir[0], oy + opp_dir[1]) if inb(ox + opp_dir[0], oy + opp_dir[1]) else (ox, oy))
            lead = od - sd  # positive is good for us
            # Prefer nearer resources among similar lead
            v = lead * 20 - sd
            if v > self_best:
                self_best = v

        # Penalize moves that move into the opponent's likely next cell (to avoid contest)
        if (nx, ny) == (ox + opp_dir[0], oy + opp_dir[1]):
            deniable_line_pen = 120

        # Soft obstacle/space: prefer increasing distance from obstacles a bit
        min_obst = 99
        for ob in obs_set:
            d = abs(ob[0] - nx) + abs(ob[1] - ny)
            if d < min_obst:
                min_obst = d
        space = min_obst

        score = self_best + on_res * 500 - deniable_line_pen + space * 2

        # Deterministic tie-break by move order
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If all moves were blocked (rare), stay
    return [best_move[0], best_move[1]]