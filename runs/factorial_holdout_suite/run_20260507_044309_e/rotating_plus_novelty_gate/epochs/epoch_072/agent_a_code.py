def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    res_set = set(tuple(r) for r in resources)

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    if res_set:
        for dx, dy, nx, ny in valid:
            if (nx, ny) in res_set:
                return [dx, dy]

    # If no resources visible, just drift toward opponent side to meet resources sooner.
    if not resources:
        step_x = 1 if ox > sx else (-1 if ox < sx else 0)
        step_y = 1 if oy > sy else (-1 if oy < sy else 0)
        for dx, dy, nx, ny in valid:
            if dx == step_x and dy == step_y:
                return [dx, dy]
        return [valid[0][0], valid[0][1]]

    best_overall = None
    best_move = [0, 0]

    for dxm, dym, nxs, nys in valid:
        # Evaluate best target after this move; reward beating opponent and approaching low-time targets.
        best_val = -10**9
        for rx, ry in resources:
            dme = cheb(nxs, nys, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Beat-opponent priority; also prefer nearer targets if tie.
            val = (do - dme) * 100 - dme
            # Mild "resource funnel" toward opponent position direction.
            val += -0.5 * cheb(nxs, nys, ox, oy)
            if (rx, ry) in res_set:
                val += 5
            if val > best_val:
                best_val = val
        # Prefer not to step away from currently best opportunity (stability).
        if best_overall is None or best_val > best_overall:
            best_overall = best_val
            best_move = [dxm, dym]
        elif best_val == best_overall:
            # Deterministic tie-break: smaller cheb to opponent, then lexicographic move.
            cur = cheb(nxs, nys, ox, oy)
            prev = cheb(sx + best_move[0], sy + best_move[1], ox, oy)
            if cur < prev or (cur == prev and (dxm, dym) < (best_move[0], best_move[1])):
                best_move = [dxm, dym]

    return [int(best_move[0]), int(best_move[1])]