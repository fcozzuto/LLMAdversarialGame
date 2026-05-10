def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    if ("evad" in self_role) or self_role == "evader":
        mode = "evade"
    elif ("purs" in self_role) or self_role == "pursuer":
        mode = "pursue"
    else:
        mode = "pursue" if ("evad" in opponent_role) or opponent_role == "evader" else "evade"

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def blocked(x, y):
        return (x, y) in obs

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)

        free_adj = 0
        for adx, ady in deltas:
            ax, ay = nx + adx, ny + ady
            if inb(ax, ay) and not blocked(ax, ay):
                free_adj += 1

        corner_bonus = 0
        if (nx in (0, w - 1)) and (ny in (0, h - 1)):
            corner_bonus = 1

        # One-step look: how good/bad is the next move for the opposing objective?
        # If we are evading, penalize moves that let the pursuer have a better approach than us.
        # If we are pursuing, reward moves that reduce opponent distance and limit their escape.
        if mode == "pursue":
            score = (-d, free_adj, corner_bonus)
            # maximize
        else:
            # minimize pursuer's best next approach (approx by assuming they move greedily towards us)
            purs_best = None
            for pdx, pdy in deltas:
                px, py = ox + pdx, oy + pdy
                if inb(px, py) and not blocked(px, py):
                    nd = dist2(px, py, nx, ny)
                    if purs_best is None or nd < purs_best:
                        purs_best = nd
            if purs_best is None:
                purs_best = d
            score = (d, -purs_best, free_adj, corner_bonus)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]