def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    tr = int(observation.get("turns_remaining", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    if not resources:
        return [0, 0]

    obs_set = set((x, y) for x, y in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick a target: prioritize resources we can reach/lead on.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # If both are too far, still allow if we strongly lead.
        if myd > tr + 4 and opd > tr + 4 and (opd - myd) < 2:
            continue
        lead = myd <= opd  # True if not behind
        contest = (opd - myd) if (opd - myd) > 0 else 0
        key = (
            1 if lead else 0,
            contest,                 # more lead better
            -(myd),                  # closer better
            -(rx * 10 + ry),        # deterministic tie-break
        )
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        best = resources[0]
    tx, ty = best

    # Move selection: 1-step lookahead to avoid obstacles and reduce distance to target.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic preference order refinement: prefer straight/diagonal toward target.
    pref = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs_set:
            pref.append((dx, dy))
    if not pref:
        pref = [(0, 0)]
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) in obs_set:
                continue
            if inb(nx, ny):
                pref.append((dx, dy))
    if not pref:
        return [0, 0]

    best_move = (0, 0)
    best_val = None
    for dx, dy in pref:
        nx, ny = sx + dx, sy + dy
        md = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Avoid allowing opponent to be closer in the next step; also avoid loops.
        loop_pen = 2 if (nx == sx and ny == sy) else 0
        opp_pen = 5 if od < md else 0
        val = (opp_pen, md, loop_pen, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]