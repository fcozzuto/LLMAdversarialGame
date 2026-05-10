def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = map(int, observation.get("self_position") or [0, 0])
    ox, oy = map(int, observation.get("opponent_position") or [0, 0])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    i_am_evader = ("evader" in self_role) or ("pursuer" in self_role and "evader" in opp_role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    tie_pref = {(0, 0): 8, (-1, -1): 0, (0, -1): 1, (1, -1): 2, (-1, 0): 3, (1, 0): 4, (-1, 1): 5, (0, 1): 6, (1, 1): 7}

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist2(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    best_val = None
    best_move = [0, 0]

    if i_am_evader:
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        tx, ty = ox, oy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_opp = dist2(nx, ny, ox, oy)
        d_target = dist2(nx, ny, tx, ty)

        if i_am_evader:
            val = (d_opp, -d_target)  # maximize distance from pursuer, also drift toward far corner
        else:
            val = (-d_opp, -d_target)  # minimize distance to pursuer/opponent position

        if best_val is None:
            best_val, best_move = val, [dx, dy]
        else:
            if val > best_val:
                best_val, best_move = val, [dx, dy]
            elif val == best_val:
                if tie_pref[(dx, dy)] < tie_pref[(best_move[0], best_move[1])]:
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]