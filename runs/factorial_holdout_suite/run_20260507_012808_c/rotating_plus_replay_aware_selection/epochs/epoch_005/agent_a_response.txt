def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    # If no resources, drift to the opposite-center corner to reduce path conflict.
    if not resources:
        tx, ty = (w - 1, 0) if sx <= w // 2 else (0, h - 1)
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d = dist((nx, ny), (tx, ty))
            cand = (d, nx, ny)
            if best is None or cand < best[0]:
                best = (cand, (dx, dy))
        return [best[1][0], best[1][1]]

    # Evaluate each possible one-step move by the best resource we can secure next.
    # Primary: we want positions where we are closer than opponent (opp_d - self_d high).
    # Secondary: smaller self distance (arrive sooner).
    # Tertiary: prefer moving that decreases distance to the currently best resource directionally.
    best_move = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        move_score = None
        for rx, ry in resources:
            self_d = dist((nx, ny), (rx, ry))
            opp_d = dist((ox, oy), (rx, ry))
            # Encourage "secure" targets (self_d <= opp_d), otherwise still consider if close to becoming secure.
            secure_bonus = 20 if self_d <= opp_d else 0
            # Penalize long self_d to avoid wasting turns.
            cand = (secure_bonus + (opp_d - self_d), -self_d, abs(rx - nx) + abs(ry - ny), rx, ry)
            if move_score is None or cand > move_score:
                move_score = cand
        # Small deterministic tie-break: prefer minimal movement magnitude then lexicographic.
        tie = (abs(dx) + abs(dy), dx, dy)
        overall = (move_score, tie)
        if best_score is None or overall > best_score:
            best_score = overall
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]