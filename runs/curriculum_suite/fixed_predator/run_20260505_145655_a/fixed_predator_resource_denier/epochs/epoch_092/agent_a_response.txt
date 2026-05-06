def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Evaluate moves directly (deterministic): choose the move that maximizes our advantage over resources.
    best_move = (0, 0, -10**18)
    # Deterministic iteration order: prefer staying then N->S->E->W then diagonals to reduce oscillation.
    deltas = [(0,0),(0,-1),(0,1),(-1,0),(1,0),(-1,-1),(1,-1),(-1,1),(1,1)]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        # Main objective: maximize "we are closer than opponent" margin with a slight distance cost.
        best_val = -10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Encourage resources opponent can’t reach first; penalize our own distance strongly.
            val = (od - sd) * 14 - sd - (rx * 0.001 + ry * 0.001)
            if val > best_val:
                best_val = val

        # Secondary: if margins are similar, avoid moving closer to opponent (resource denial).
        opp_closeness = man(nx, ny, ox, oy)
        # Tie-break: prefer positions closer to center slightly.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center = abs(nx - cx) + abs(ny - cy)
        score = best_val - 0.15 * opp_closeness - 0.01 * center

        if score > best_move[2]:
            best_move = (dx, dy, score)

    return [int(best_move[0]), int(best_move[1])]