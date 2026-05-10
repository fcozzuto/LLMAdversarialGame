def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("purs" in opp_role and "evad" not in self_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def d2(x1, y1, x2, y2):
        dx, dy = x1-x2, y1-y2
        return dx*dx + dy*dy

    # penalty for being adjacent to obstacles (helps wall-run evasion and pursuer paths)
    def obs_pen(nx, ny):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx+dx, ny+dy) in obstacles:
                    pen += 1
        return pen

    best_score = None
    best_move = [0, 0]

    # Tie-breaker favors fewer steps toward/away consistently and staying deterministic
    # by fixed iteration order of moves.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        dist_opp = d2(nx, ny, ox, oy)
        penalty = obs_pen(nx, ny)

        if pursuer:
            # maximize score by minimizing distance to opponent; heavy penalty near obstacles
            score = -dist_opp - 0.15 * penalty
        else:
            # evade: maximize distance to opponent and avoid obstacles
            corners = ((0, 0), (0, h-1), (w-1, 0), (w-1, h-1))
            corner_boost = max(d2(nx, ny, cx, cy) for cx, cy in corners) * 0.01
            score = dist_opp + 0.25 * corner_boost - 0.2 * penalty

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]