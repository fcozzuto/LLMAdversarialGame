def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        # deterministic safe fallback: move that maximizes distance from opponent
        moves = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                    moves.append((dx, dy))
        if not moves:
            return [0, 0]
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - ox) + abs(ny - oy)
            key = (-d, dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [int(best[1]), int(best[2])]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy))

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Opportunistic/interceptor: choose the move that creates the biggest lead on some resource
    # Lead = (oppDist - myDist), tie-break toward shorter myDist and then lexicographic move.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        best_lead = -10**9
        best_my = 10**9
        for rx, ry in res:
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            lead = opd - myd
            if (lead > best_lead) or (lead == best_lead and myd < best_my):
                best_lead, best_my = lead, myd
        # small penalty to avoid dithering; small bonus for moving toward closer best resource
        score = (best_lead, -best_my)
        key = (-score[0], score[1], dx, dy)  # min key => best
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [int(best[1]), int(best[2])]