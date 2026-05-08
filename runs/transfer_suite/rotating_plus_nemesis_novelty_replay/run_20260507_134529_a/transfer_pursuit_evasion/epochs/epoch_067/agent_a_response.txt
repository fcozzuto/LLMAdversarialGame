def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role") or "").lower()
    opp_role = str(observation.get("opponent_role") or "").lower()
    self_evader = "evader" in self_role
    opp_evader = "evader" in opp_role

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = [(dx, dy) for dx, dy in moves if inb(sx + dx, sy + dy)]

    if not legal:
        legal = [(0, 0)]

    def predict_opp(ourx, oury):
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if not inb(nx, ny):
                continue
            if nx == ourx and ny == oury:
                v = 10**9 if opp_evader else -10**9
            else:
                v = dist(ourx, oury, nx, ny)
                v = -v if (not opp_evader) else v  # pursuer(chase)->min distance => negative; evader(run)->max => positive
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        if best is None:
            best = (0, 0)
        return ox + best[0], oy + best[1]

    # If we're pursuer, choose move minimizing capture risk (maximize negative distance to predicted opponent position).
    # If we're evader, choose move maximizing distance from predicted opponent position.
    best_move = (0, 0)
    best_score = None
    for dx, dy in legal:
        nsx, nsy = sx + dx, sy + dy
        pred_ox, pred_oy = predict_opp(nsx, nsy)

        if nsx == pred_ox and nsy == pred_oy:
            score = 10**9 if (not self_evader) else -10**9
        else:
            d = dist(nsx, nsy, pred_ox, pred_oy)
            score = -d if (not self_evader) else d

        # Deterministic tie-breaker: fixed move ordering already in moves list; update only on strictly better.
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]