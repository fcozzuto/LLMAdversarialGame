def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or (("evad" not in self_role) and ("evad" in opp_role) is False)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx*dx + dy*dy

    # Choose a corner target that matches the role behavior.
    if is_pursuer:
        # When chasing, avoid long detours: also bias toward reducing opponent's distance to the nearest corner.
        target_corner = min(corners, key=lambda c: abs(ox - c[0]) + abs(oy - c[1]))
    else:
        # When evading, bias toward the farthest corner from the pursuer.
        target_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    best_score = None
    best = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d_to_opp = dist2(nx, ny, ox, oy)
        if is_pursuer:
            # Primary: minimize distance to opponent.
            # Secondary: push opponent away from its nearest corner.
            d_opp_to_corner = abs(ox - target_corner[0]) + abs(oy - target_corner[1])
            score = d_to_opp - 0.1 * d_opp_to_corner
        else:
            # Primary: maximize distance from pursuer.
            # Secondary: move toward a chosen corner target.
            d_from_pursuer = d_to_opp
            d_corner = dist2(nx, ny, target_corner[0], target_corner[1])
            score = -d_from_pursuer + 0.02 * d_corner

        if best_score is None:
            best_score = score
            best = [dx, dy]
        else:
            if is_pursuer:
                if score < best_score:
                    best_score = score
                    best = [dx, dy]
            else:
                if score < best_score:
                    best_score = score
                    best = [dx, dy]

    return [int(best[0]), int(best[1])]