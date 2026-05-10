def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    gw, gh = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    def diag_dist(x1, y1, x2, y2):
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        return dx if dx > dy else dy
    def obstacle_ahead(x, y):
        # penalize moves adjacent to obstacles to reduce hits
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose a target resource where we have an advantage; else choose nearest overall.
    best = None  # (priority, sx_dist, ox_dist, rx, ry)
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        sd = diag_dist(sx, sy, rx, ry)
        od = diag_dist(ox, oy, rx, ry)
        adv = od - sd  # positive if we are closer (deterministic tie handled below)
        # If tied/behind, still consider, but lower priority.
        priority = 1000 * (1 if adv > 0 else 0) + adv
        cand = (priority, sd, od, rx, ry)
        if best is None or cand > best:
            best = cand
    _, _, _, tx, ty = best

    # Move scoring: approach target; if opponent is closer to the same target, slightly bias toward resources nearer to us.
    cand_resource = best[3], best[4]
    tdist_self = diag_dist(sx, sy, cand_resource[0], cand_resource[1])
    oppdist = diag_dist(ox, oy, cand_resource[0], cand_resource[1])

    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        approach = -diag_dist(nx, ny, tx, ty)
        obst = -0.7 * obstacle_ahead(nx, ny)
        # If opponent is close to the target, encourage moves that reduce distance gap.
        if oppdist - tdist_self > 0:
            gap = (diag_dist(ox, oy, tx, ty) - diag_dist(nx, ny, tx, ty))
            opp_bias = 0.6 * gap
        else:
            opp_bias = 0.0
        # Small deterministic tie-break: prefer moves with smaller x then y offsets magnitude.
        tie = -(abs(dx) * 0.01 + abs(dy) * 0.001)
        score = approach + obst + opp_bias + tie
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    # Safety fallback: if all invalid, stay.
    if best_score is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]