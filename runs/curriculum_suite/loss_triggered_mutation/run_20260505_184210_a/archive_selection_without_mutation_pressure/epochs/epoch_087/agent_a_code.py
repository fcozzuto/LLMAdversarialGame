def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        # Center-seeking + mild denial to opponent line
        cx, cy = (w - 1) // 2, (h - 1) // 2
        target = (cx, cy)
        # If far, also bias away from direct chase to avoid collision with denier routes
        if dist((sx, sy), target) > 6:
            if ox < sx: target = (sx - 1 if sx - 1 >= 0 else sx, cy)
            elif ox > sx: target = (sx + 1 if sx + 1 < w else sx, cy)
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            score = dist((nx, ny), target) - 0.15 * dist((nx, ny), (ox, oy))
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Intercept/deny: choose resource maximizing (opp_reach - us_reach), but ensure we still move toward it.
    # If multiple, deterministically choose by resource distance and coordinate tie-break.
    best_move = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        me = (nx, ny)
        best_for_move = None
        for r in resources:
            dr_me = dist(me, r)
            dr_opp = dist((ox, oy), r)
            # If we can reach sooner, prioritize heavily; otherwise choose closer denial.
            rel = dr_opp - dr_me
            # Prefer nearer immediate value, slight penalty if moving away from currently favored resources.
            val = -rel * 3.0 + dr_me * 0.25
            if best_for_move is None or (val, r[0], r[1]) < (best_for_move[0], best_for_move[1], best_for_move[2]):
                best_for_move = (val, r[0], r[1])
        # Also add local obstacle/edge safety: avoid steps that make it hard next turn by maximizing mobility
        mobility = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if inside(tx, ty):
                mobility += 1
        move_score = best_for_move[0] - mobility * 0.08
        if best_move is None or (move_score, dx, dy) < (best_move[0], best_move[1], best_move[2]):
            best_move = (move_score, dx, dy)

    return [best_move[1], best_move[2]]