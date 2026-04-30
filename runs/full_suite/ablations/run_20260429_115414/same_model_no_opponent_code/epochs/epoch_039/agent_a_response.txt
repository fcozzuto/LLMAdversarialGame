def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
    if not res:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    opp = (ox, oy)

    best = None
    best_score = -10**18
    # Tie-break deterministically by ordering of candidates
    candidates.sort(key=lambda t: (t[0], t[1], t[2], t[3]))

    for dx, dy, nx, ny in candidates:
        me = (nx, ny)
        self_dmin = 10**9
        opp_closer_penalty = 0
        lead = 0
        for r in res:
            ds = dist(me, r)
            do = dist(opp, r)
            if ds < self_dmin:
                self_dmin = ds
            if do < ds:
                # prefer resources we can beat, penalize those opponent can reach first
                opp_closer_penalty += (ds - do)
            else:
                lead = max(lead, do - ds)
        score = (lead * 2.0) - (self_dmin * 1.0) - (opp_closer_penalty * 0.15)
        # Mild bias toward progressing away from corners that could be stalemates
        score += 0.01 * ((nx + ny) - (sx + sy))
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]