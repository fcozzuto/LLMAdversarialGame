def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # pick a "focus" resource deterministically for tie-breaking
    best_res = None
    for rx, ry in resources:
        myd = md(sx, sy, rx, ry)
        opd = md(ox, oy, rx, ry)
        lead = opd - myd  # positive => I arrive first
        key = (lead, -myd, -rx, -ry)
        if best_res is None or key > best_res[0]:
            best_res = (key, (rx, ry))
    _, (tx, ty) = best_res

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # evaluate next position: favor immediate capture, then winning leads, then head toward focus
    best = None
    for dx, dy, nx, ny in candidates:
        capture = 1 if (nx, ny) in resources else 0
        # compute best lead among top few resources deterministically (no sorting)
        best_lead = -10**9
        best_myd = 10**9
        best_rxry = (0, 0)
        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            lead = opd - myd
            if lead > best_lead or (lead == best_lead and (myd < best_myd or (myd == best_myd and (-rx, -ry) > (-best_rxry[0], -best_rxry[1])))):
                best_lead, best_myd, best_rxry = lead, myd, (rx, ry)
        # secondary preference: move closer to focus target if not already winning by leads
        focus_d = md(nx, ny, tx, ty)
        key = (capture, best_lead, -best_myd, -focus_d, dx, dy, nx, ny)
        if best is None or key > best[0]:
            best = (key, [dx, dy])
    return best[1]