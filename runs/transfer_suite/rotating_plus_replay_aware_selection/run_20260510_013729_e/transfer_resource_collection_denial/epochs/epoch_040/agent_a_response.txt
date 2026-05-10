def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(x, y) for x, y in obstacles}
    if not resources:
        return [0, 0]

    cand = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_adv_for_cell(x, y):
        best = None
        for rx, ry in resources:
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive: we are closer or tie (good under denier)
            # Prefer immediate captures, then best lead, then slightly far from opponent to avoid giving them tempo.
            oppd = cheb(x, y, ox, oy)
            key = (lead, -ds, oppd, -(rx * 8 + ry))
            if best is None or key > best:
                best = key
        return best[0], best[1], best[2]  # lead, -ds, oppd

    best_move = (0, 0)
    best_key = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            nx, ny = sx, sy  # deterministic: invalid move becomes stay
        lead, neg_ds, oppd = best_adv_for_cell(nx, ny)
        # Extra tie-break: if lead is equal, avoid stepping closer to opponent unless it improves ds.
        step_opp = cheb(nx, ny, ox, oy)
        key = (lead, neg_ds, step_opp, -(abs(nx-ox) + abs(ny-oy)))
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]