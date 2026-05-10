def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obst = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("evader" not in self_role) and ("purs" in self_role or self_role == "")
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in obst
    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy
    def edge_pen(x, y):
        # small tie-breaker to avoid hugging edges unless helpful
        return min(x, w - 1 - x, y, h - 1 - y)
    my_cands = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            my_cands.append((dx, dy, nx, ny))
    if not my_cands:
        return [0, 0]
    # Opponent model: if we are pursuer, opponent is evader (maximizes our distance).
    # If we are evader, opponent is pursuer (minimizes our distance).
    def opp_best_response(them_x, them_y, my_x_after, my_y_after):
        best = None
        for txd, tyd in dirs:
            nx, ny = them_x + txd, them_y + tyd
            if not legal(nx, ny):
                continue
            d = dist2(my_x_after, my_y_after, nx, ny)
            # evader: maximize distance, pursuer: minimize distance
            if pursuer:
                key = (d, edge_pen(nx, ny))  # prefer more room (tie-break)
                if best is None or key > best[0]:
                    best = (key, (txd, tyd, nx, ny))
            else:
                key = (-d, edge_pen(nx, ny))
                if best is None or key > best[0]:
                    best = (key, (txd, tyd, nx, ny))
        if best is None:
            return 0, 0, them_x, them_y
        return best[1]
    best_move = None
    best_score = None
    for dx, dy, nx, ny in my_cands:
        txd, tyd, pnx, pny = opp_best_response(ox, oy, nx, ny)
        d = dist2(nx, ny, pnx, pny)
        # Choose our move to minimize distance if pursuer; maximize if evader.
        if pursuer:
            score = (d, -edge_pen(nx, ny))  # minimize distance, keep some mobility
            if best_score is None or score < best_score:
                best_score = score
                best_move = [dx, dy]
        else:
            score = (-d, -edge_pen(nx, ny))  # maximize distance
            if best_score is None or score < best_score:
                best_score = score
                best_move = [dx, dy]
    return best_move if best_move is not None else [0, 0]