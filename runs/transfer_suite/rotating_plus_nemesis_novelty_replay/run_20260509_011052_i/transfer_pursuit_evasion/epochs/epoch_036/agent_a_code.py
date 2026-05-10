def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = list(map(tuple, observation.get("resources") or []))
    self_role = (observation.get("self_role") or "").lower()

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        # Pick nearest resource to me; if multiple, tie-break by x,y for determinism.
        best = None
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            key = (d, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = ox, oy

    evader = ("evader" in self_role) and ("pursuer" not in self_role)
    pursuer = ("pursuer" in self_role)

    opp_mode = "avoid" if evader and not pursuer else "chase"
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_me = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)

        val = 0
        if resources:
            # Prefer moving toward target resource; reward when closer.
            val += 2000 - 50 * d_me
        else:
            val += 0

        # Opponent influence
        if opp_mode == "avoid":
            val += 120 * d_opp
        else:
            val += -120 * d_opp

        # Mild preference for staying if values tie (deterministic via dir order already)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]