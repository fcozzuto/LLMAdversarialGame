def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_evader = ("evad" in self_role) or ("runner" in self_role) or ("evasion" in self_role) or (self_role == "evader")
    pursuing = (not self_evader) or (("evad" in opp_role) or ("runner" in opp_role) or ("evasion" in opp_role) or (opp_role == "evader"))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Predict opponent's next move as best response to our candidate (deterministic).
    def predict_opp(selfx, selfy):
        best = None
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if not valid(nx, ny):
                nx, ny = ox, oy
            ddx, ddy = selfx - nx, selfy - ny
            dist2 = ddx * ddx + ddy * ddy
            # Evader maximizes distance.
            cand = dist2
            if best is None or cand > best[0] or (cand == best[0] and (dx, dy) < best[1]):
                best = (cand, (dx, dy), nx, ny)
        return best[2], best[3]

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        if pursuing:
            px, py = predict_opp(nx, ny)
            ddx, ddy = nx - px, ny - py
            dist2 = ddx * ddx + ddy * ddy
            # Smaller is better for pursuer; slight preference for reducing current distance too.
            curdx, curdy = nx - ox, ny - oy
            curd2 = curdx * curdx + curdy * curdy
            score = dist2 * 1000 + curd2
            better = best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move)
        else:
            ddx, ddy = nx - ox, ny - oy
            dist2 = ddx * ddx + ddy * ddy
            score = -dist2
            better = best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move)
        if better:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]