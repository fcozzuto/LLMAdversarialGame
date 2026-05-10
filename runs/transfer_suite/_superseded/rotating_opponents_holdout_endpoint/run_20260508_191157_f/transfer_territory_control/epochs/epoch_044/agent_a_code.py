def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    resources = set(map(tuple, observation.get("resources") or []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    # Prefer flipping: go to an opponent-controlled cell; otherwise take nearby unclaimed/resource.
    if opp_t:
        # Bias toward cells closer to opponent too (likely on the edge).
        tx, ty = min(opp_t, key=lambda c: 2 * (abs(c[0] - sx) + abs(c[1] - sy)) + (abs(c[0] - ox) + abs(c[1] - oy)))
    elif unclaimed:
        tx, ty = min(unclaimed, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
    elif resources:
        tx, ty = min(resources, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
    else:
        tx, ty = ox, oy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        # Score: maximize flip potential, minimize distance to target, and avoid stepping into blocked-free "dead ends" near obstacles.
        flip = 1 if (nx, ny) in opp_t else 0
        dist = abs(nx - tx) + abs(ny - ty)
        # Small deterministic obstacle penalty
        adj_block = 0
        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ax, ay = nx + ddx, ny + ddy
            if not (0 <= ax < w and 0 <= ay < h) or (ax, ay) in blocked:
                adj_block += 1
        score = 1000 * flip - 3 * dist - adj_block
        # Tie-break deterministically by favoring moves that reduce dx then dy magnitude
        if score > best_score or (score == best_score and (abs(dx), abs(dy), dx, dy) < (abs(best_move[0]), abs(best_move[1]), best_move[0], best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]