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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score_move(nx, ny):
        d = dist2(nx, ny, ox, oy)
        if i_am_evader:
            # Prefer increasing distance; penalize being near obstacles to avoid getting boxed.
            adj_obs = 0
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                ax, ay = nx + dx, ny + dy
                if not valid(ax, ay):
                    adj_obs += 1
            return d - 0.6 * adj_obs
        else:
            # Pursuer: reduce distance; also avoid obstacle adjacency.
            adj_obs = 0
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                ax, ay = nx + dx, ny + dy
                if not valid(ax, ay):
                    adj_obs += 1
            return -d - 0.6 * adj_obs

    # One-step lookahead: choose move that gives best score against the opponent's immediate greedy step.
    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        own_val = score_move(nx, ny)

        # Predict opponent response: greedy toward our current position if pursuer; away if evader.
        opp_pref_evade = not i_am_evader
        opp_best_d = None
        for odx, ody in dirs:
            tx, ty = ox + odx, oy + ody
            if not valid(tx, ty):
                continue
            d = dist2(tx, ty, nx, ny)
            if opp_best_d is None:
                opp_best_d = d
            else:
                if opp_pref_evade:
                    if d > opp_best_d:
                        opp_best_d = d
                else:
                    if d < opp_best_d:
                        opp_best_d = d

        # If opponent can worsen our objective, penalize; otherwise slight boost.
        if opp_best_d is None:
            look = own_val
        else:
            if i_am_evader:
                look = own_val + 0.15 * opp_best_d
            else:
                look = own_val - 0.15 * opp_best_d

        if best_val is None or (look > best_val if i_am_evader else look > best_val):
            best_val = look
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]