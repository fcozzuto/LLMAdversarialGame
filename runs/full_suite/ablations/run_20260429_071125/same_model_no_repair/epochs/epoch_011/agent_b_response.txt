def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = set((p[0], p[1]) for p in obstacles)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    adj4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    adj8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def hazard(x, y):
        c = 0
        for dx, dy in adj4:
            if (x + dx, y + dy) in occ: c += 1
        if (x, y) in occ: c += 4
        return c

    def opp_pressure_to(rx, ry):
        # positive means opponent is closer to this resource
        return man(ox, oy, rx, ry) - man(sx, sy, rx, ry)

    # Target: contest the resource opponent most strongly has access to.
    target = None
    best_contest = None
    if resources:
        for rx, ry in resources:
            opp_gain = opp_pressure_to(rx, ry)
            # We want to maximize (how much more opponent is favored), then prefer nearby to us to reduce distance.
            key = (-opp_gain, man(sx, sy, rx, ry), ry, rx)
            # Actually choose resource where opponent is closer -> opp_gain negative; maximize contest => smallest -opp_gain.
            if best_contest is None or key < best_contest:
                best_contest = key
                target = (rx, ry)

    if target is None:
        # No resources: drift toward center while avoiding obstacles.
        tx, ty = w // 2, h // 2
    else:
        tx, ty = target

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in occ:
            score = -10**9
        else:
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            # Contest while keeping distance from opponent: prioritize making our distance shrink vs theirs.
            contest = od - sd
            # Also reward getting closer relative to other resources by small secondary term.
            close_center = -man(nx, ny, w // 2, h // 2)
            opp_adj = 0
            for ax, ay in adj8:
                if (nx + ax, ny + ay) == (ox, oy): opp_adj += 1
            score = contest * 5 + close_center - hazard(nx, ny) * 3 - opp_adj * 2
        key = (score, -abs(dx) - abs(dy), dx, dy)
        if best_score is None or key > best_score:
            best_score = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]