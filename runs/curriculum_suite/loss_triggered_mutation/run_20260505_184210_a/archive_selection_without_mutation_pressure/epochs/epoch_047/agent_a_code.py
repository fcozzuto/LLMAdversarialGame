def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cd(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    # If resources exist: pick move that minimizes our distance to best resource while keeping opponent far from that same target.
    if resources:
        best = None
        best_score = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            # pick target resource that is best for us after this move (tie: closer then coordinates)
            best_r = None
            best_rd = None
            for r in resources:
                rx, ry = r
                d = cd(nx, ny, rx, ry)
                if best_rd is None or d < best_rd or (d == best_rd and (rx, ry) < best_r):
                    best_rd = d
                    best_r = (rx, ry)
            rx, ry = best_r
            our_d = best_rd
            opp_d = cd(ox, oy, rx, ry)
            # Prefer smaller our_d; and larger opp_d to reduce their access to our target.
            score = our_d * 100 - opp_d
            if best_score is None or score < best_score or (score == best_score and (dx, dy) < best):
                best_score = score
                best = (dx, dy)
        return [best[0], best[1]]

    # No resources: drift toward opponent to deny time, but still avoid obstacles.
    best = None
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = cd(nx, ny, ox, oy)
        score = d * 10 + (dx * 0 + dy * 0)  # deterministic tie-break via (dx,dy)
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]]