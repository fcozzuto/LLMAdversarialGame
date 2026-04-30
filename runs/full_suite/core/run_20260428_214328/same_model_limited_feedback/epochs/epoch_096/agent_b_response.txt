def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        # move toward center deterministically
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = None; bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: continue
            v = (abs(nx - tx) + abs(ny - ty), abs(ox - nx) + abs(oy - ny))
            if best is None or v < bestv: best = (dx, dy); bestv = v
        return list(best if best is not None else (0, 0))
    def dist(a, b): 
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    # Choose candidate target resources using deterministic tie-breaking
    scored_targets = []
    for rx, ry in resources:
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Prefer where we can arrive not later; otherwise reduce disadvantage.
        pref = ds - do
        # Also prefer closer absolute targets when pref equal
        scored_targets.append((pref, ds, rx, ry))
    scored_targets.sort()
    # Use up to few top targets for robustness without heavy search
    candidates = scored_targets[:min(6, len(scored_targets))]
    def eval_next(nx, ny):
        best_local = None
        for pref, ds, rx, ry in candidates:
            dsn = dist((nx, ny), (rx, ry))
            don = dist((ox, oy), (rx, ry))  # opponent hasn't moved this turn
            # If opponent is threatening, we bias to targets where we can overtake
            v = (dsn - don, dsn, pref, abs(nx - ox) + abs(ny - oy), rx, ry)
            if best_local is None or v < best_local: best_local = v
        # Prefer not staying adjacent to opponent unless it also improves target score
        return best_local[0], best_local[1], best_local[3], best_local[4], best_local[5]
    best_move = (0, 0); best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles: continue
        # Extra penalty for moves that step into immediate capture race: if opponent can reach this tile in 1
        opp_reach = max(abs(nx - ox), abs(ny - oy)) <= 1
        v = eval_next(nx, ny)
        v2 = (v[0], v[1], v[2] + (1 if opp_reach else 0), v[3], v[4], dx, dy)
        if best_val is None or v2 < best_val:
            best_val = v2; best_move = (dx, dy)
    return [best_move[0], best_move[1]]