def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    i_am_pursuer = ("purs" in self_role) or ("chase" in self_role) or ("hunter" in self_role)
    if not i_am_pursuer:
        if ("purs" in opp_role) or ("chase" in opp_role) or ("hunter" in opp_role):
            i_am_pursuer = False
        else:
            i_am_pursuer = ("evad" not in self_role) and ("escap" not in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    def step_targets(px, py, target_is_far):
        bestd = None
        best = []
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)  # distance to our current position (used only for opponent estimation)
            if target_is_far:
                score = d
            else:
                score = -d
            if bestd is None or score > bestd:
                bestd = score
                best = [(nx, ny)]
            elif score == bestd:
                best.append((nx, ny))
        return best[0] if best else (px, py)

    # Predict opponent one step based on likely objective (evader maximizes distance, pursuer minimizes).
    opp_target_far = i_am_pursuer  # if we are pursuer, opponent is likely evader -> farthest move
    # If roles unknown/mismatched, we still use this heuristic complementarily.
    predicted_ox, predicted_oy = step_targets(ox, oy, target_is_far=opp_target_far)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_pred = dist2(nx, ny, predicted_ox, predicted_oy)
        # Secondary terms: obstacle "pressure" and corner-avoidance for zigzag trapping.
        adj_block = 0
        for ddx, ddy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            axx, ayy = nx + ddx, ny + ddy
            if not (0 <= axx < w and 0 <= ayy < h) or (axx, ayy) in obstacles:
                adj_block += 1

        # Also discourage letting opponent escape to extreme corners when we are pursuer.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        corner_min = None
        for cx, cy in corners:
            d = dist2(nx, ny, cx, cy)
            corner_min = d if corner_min is None else (d if d < corner_min else corner_min)

        if i_am_pursuer:
            score = (-d_pred, -adj_block, corner_min)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        else:
            # Evader: maximize distance to predicted pursuer target; avoid being boxed near obstacles.
            score = (d_pred, -adj_block, -corner_min)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]