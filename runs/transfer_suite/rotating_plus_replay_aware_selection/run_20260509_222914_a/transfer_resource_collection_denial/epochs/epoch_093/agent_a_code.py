def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    best_move = (0, 0)
    best_val = None
    best_tiebreak = None

    ti = int(observation.get("turn_index", 0) or 0)
    # Deterministic slight preference to avoid repeating patterns
    move_pref = moves[(ti % len(moves)):] + moves[:(ti % len(moves))]

    for dx, dy in move_pref:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy

        # Evaluate best "capture line" among all resources from the next position
        chosen = None
        for rx, ry in resources:
            self_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            if self_d <= opp_d:
                # Prefer guaranteed/earlier grabs; maximize slack (opp-self), then minimize self_d
                val = (10**6 + (opp_d - self_d), -self_d)
            else:
                # Avoid resources where opponent is clearly closer; still consider if no better exists
                val = (-(self_d - opp_d), -self_d)
            if chosen is None or val > chosen[0]:
                chosen = (val, self_d, rx, ry)

        cur_val, cur_sd, rx, ry = chosen
        tiebreak = (cur_sd, rx, ry)
        if best_val is None or cur_val > best_val or (cur_val == best_val and tiebreak < best_tiebreak):
            best_val = cur_val
            best_tiebreak = tiebreak
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]