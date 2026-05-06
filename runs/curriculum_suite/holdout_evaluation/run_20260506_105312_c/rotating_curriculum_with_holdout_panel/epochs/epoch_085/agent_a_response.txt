def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    rlist = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                rlist.append((x, y))

    if not rlist:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    # Interceptor-style: prefer states that reduce opponent's lead on the best contested resource.
    # Tie-break deterministically by (advantage, -opp_dist, -self_dist, dx, dy) with small preference to moving diagonally.
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # For each resource compute lead = opp_dist - self_dist after this move; take max lead.
        max_lead = None
        best_opp = None
        best_self = None
        for rx, ry in rlist:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            lead = od - sd
            if max_lead is None or lead > max_lead or (lead == max_lead and (od < best_opp or (od == best_opp and sd < best_self))):
                max_lead = lead
                best_opp = od
                best_self = sd

        # Encourage positive leads strongly; also keep some pressure if no positive lead exists.
        # Score tuple: (primary advantage, opp proximity, self proximity, prefer diagonals, then deterministic ordering).
        diag_pref = 1 if dx != 0 and dy != 0 else 0
        score = (max_lead, -best_opp, -best_self, diag_pref, -abs(dx) - abs(dy), dx, dy)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]