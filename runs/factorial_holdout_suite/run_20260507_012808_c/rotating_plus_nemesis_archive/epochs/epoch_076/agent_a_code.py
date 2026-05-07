def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal or not resources:
        return [0, 0]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # 1-step lookahead: choose move that maximizes expected lead on best resource.
    best_global = None
    best_global_val = -10**9
    for r in resources:
        my_d = dist((sx, sy), r)
        opp_d = dist((ox, oy), r)
        lead = opp_d - my_d
        # Prefer resources where we can take earlier, and slightly prefer those closer to finish.
        val = lead * 10 + (opp_d - my_d) + (10 - my_d)
        if val > best_global_val:
            best_global_val = val
            best_global = r
    target = best_global

    # If no meaningful lead, switch to a "contested" target: minimize our distance but keep opponent farther.
    if best_global_val < 0:
        best = None
        bestv = 10**9
        for r in resources:
            my_d = dist((sx, sy), r)
            opp_d = dist((ox, oy), r)
            v = (my_d, -opp_d)  # primary: closer to us, tie-break: farther from opponent
            if v < bestv:
                bestv = v
                best = r
        target = best

    tx, ty = target
    # Evaluate moves by resulting lead and closeness to target; also bias towards reducing separation to target.
    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in legal:
        nsx, nsy = sx + dx, sy + dy
        my_d = dist((nsx, nsy), (tx, ty))
        opp_d = dist((ox, oy), (tx, ty))
        lead = opp_d - my_d
        # small anti-stall and obstacle-adjacent bias via distance-to-target reduction
        cur_d = dist((sx, sy), (tx, ty))
        step_gain = cur_d - my_d
        # if we can still improve another resource with the move, capture that too (small weight)
        alt_best = -10**9
        for r in resources:
            md = dist((nsx, nsy), r)
            od = dist((ox, oy), r)
            alt_best = max(alt_best, (od - md) * 6 + (8 - md))
        score = lead * 12 + step_gain * 3 + alt_best * 0.2
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]