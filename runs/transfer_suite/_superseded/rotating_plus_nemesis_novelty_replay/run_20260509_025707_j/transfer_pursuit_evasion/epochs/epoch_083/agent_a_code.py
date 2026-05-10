def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    i_am_evader = ("evader" in role) or ("runner" in role) or ("evasion" in role) or ("escape" in role)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Greedy with one-step lookahead: assume opponent just continues to try to improve its objective.
    best_val = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d1 = dist2(nx, ny, ox, oy)
        # If evader: maximize distance; if pursuer: minimize distance.
        my_goal = d1 if i_am_evader else -d1

        # Opponent response proxy: after our move, opponent also chooses a move that improves its goal.
        # We don't know opponent role precisely; infer from our role complement.
        opp_is_evader = not i_am_evader
        opp_best = None
        for odx, ody in dirs:
            mx, my = ox + odx, oy + ody
            if not (0 <= mx < w and 0 <= my < h) or (mx, my) in obstacles:
                continue
            d2v = dist2(nx, ny, mx, my)  # distance after opponent moves too
            opp_goal = d2v if opp_is_evader else -d2v
            if opp_best is None:
                opp_best = opp_goal
            else:
                # opponent maximizes its goal
                if opp_goal > opp_best:
                    opp_best = opp_goal

        # If no valid opponent move, use our direct goal.
        val = my_goal + (opp_best if opp_best is not None else 0) * 0.25

        # Tie-break: prefer moving closer/farther along main axis, and avoid staying still when possible.
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        axis_progress = abs((nx - ox)) + abs((ny - oy))
        # Convert axis_progress to tie-break direction consistent with our objective.
        tie = axis_progress if i_am_evader else -axis_progress
        if best_val is None:
            best_val = (val, -stay_pen, tie)
            best_move = [dx, dy]
        else:
            cand = (val, -stay_pen, tie)
            if cand > best_val:
                best_val = cand
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]