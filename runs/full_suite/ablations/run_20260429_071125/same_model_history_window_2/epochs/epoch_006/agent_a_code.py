def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not deltas:
        return [0, 0]

    # Pick a resource to contest: maximize current lead (opp_dist - self_dist), tie-break by closer resource.
    best_tgt = None
    best_lead = None
    for r in resources:
        tx, ty = r[0], r[1]
        dS = md(sx, sy, tx, ty)
        dO = md(ox, oy, tx, ty)
        lead = dO - dS
        key = (lead, -dS, -tx, -ty)
        if best_tgt is None or key > (best_lead[0], best_lead[1], best_lead[2], best_lead[3]):
            best_tgt = (tx, ty)
            best_lead = (lead, dS, tx, ty)

    if best_tgt is None:
        # No resources: move to maximize distance from opponent (deterministic).
        best_move = (0, 0)
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            val = md(nx, ny, ox, oy)
            if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    tx, ty = best_tgt

    # Evaluate each move by (a) new lead on target, (b) immediate pickup, (c) slight preference to reduce target distance.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dS = md(nx, ny, tx, ty)
        dO = md(nx, ny, ox, oy)

        on_tgt = 1 if (nx, ny) == (tx, ty) else 0
        prev_dS = md(sx, sy, tx, ty)
        prev_dO = md(sx, sy, ox, oy)
        lead = md(ox, oy, tx, ty) - dS

        # If we're behind on the target, prioritize moves that improve lead; otherwise prioritize securing.
        score = 0
        score += 2000 * on_tgt
        score += 30 * lead
        score += 2 * (prev_dS - dS)  # moving closer helps
        score += -0.2 * dO + 0.01 * (prev_dO - dO)  # keep from getting too close to opponent

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]