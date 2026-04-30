def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Select a target resource that I am likely to secure.
    best_res = None
    best_score = None
    for rx, ry in resources:
        myd = kdist(sx, sy, rx, ry)
        opd = kdist(ox, oy, rx, ry)
        # Prefer closer resources; strongly avoid ones opponent can reach sooner/equal.
        score = myd + (0 if opd > myd else -10) + (2 if opd < myd else 0)
        # Slightly bias toward resources nearer the opponent only when I'm not behind.
        if opd > myd:
            score -= 1
        if best_score is None or score < best_score:
            best_score = score
            best_res = (rx, ry)

    if best_res is None:
        # No resources: move away from opponent or hold safe.
        dx = 0
        dy = 0
        best = None
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if not valid(nx, ny):
                continue
            d = kdist(nx, ny, ox, oy)
            if best is None or d > best:
                best = d
                dx, dy = mx, my
        return [dx, dy]

    rx, ry = best_res
    best_move = (0, 0)
    best_move_score = None
    # If resources are on top of us, we will naturally choose a move that stays/takes it.
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not valid(nx, ny):
            continue
        myd = kdist(nx, ny, rx, ry)
        opd = kdist(ox, oy, rx, ry)

        # Also consider "contesting" if opponent is close to the same target: reduce their approach.
        contest = 0
        if opd <= myd + 1:
            # Try to increase distance between opponent and me slightly while staying on course.
            contest = -kdist(nx, ny, ox, oy)

        # Prefer reducing my distance to target; avoid stepping closer to obstacles is not possible without full search.
        move_score = myd * 10 + (0 if opd > myd else -100) + contest
        if best_move_score is None or move_score < best_move_score:
            best_move_score = move_score
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]