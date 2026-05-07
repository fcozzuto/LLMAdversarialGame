def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dxs = [-1, 0, 1]
    dys = [-1, 0, 1]
    moves = [(dx, dy) for dx in dxs for dy in dys if not (dx == 0 and dy == 0)] + [(0, 0)]

    if not resources:
        tx, ty = w // 2, h // 2
        best_move, best_val = [0, 0], None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            val = (cheb(nx, ny, tx, ty), cheb(nx, ny, ox, oy))
            if best_val is None or val < best_val:
                best_val, best_move = val, [dx, dy]
        return best_move

    best_target = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # If opponent is closer, deprioritize; otherwise prioritize larger advantage.
        advantage = do - ds
        # Slightly prefer targets that are "less contested" and not too far.
        key = (-advantage, ds, do, cheb(sx, sy, rx, w - 1 - rx), rx, ry)
        if best_key is None or key < best_key:
            best_key, best_target = key, (rx, ry)

    tx, ty = best_target
    opp_toward = None
    if resources:
        # Estimate opponent's likely target for blocking: closest resource from opponent.
        bestd, opp_toward = None, None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = cheb(ox, oy, rx, ry)
            if bestd is None or d < bestd:
                bestd, opp_toward = d, (rx, ry)

    def goal_value(nx, ny):
        myd = cheb(nx, ny, tx, ty)
        opp_penalty = 0
        if opp_toward is not None:
            oppd = cheb(nx, ny, opp_toward[0], opp_toward[1])
            opp_penalty = cheb(ox, oy, tx, ty) <= cheb(nx, ny, tx, ty) and oppd < myd
        # Move to reduce my distance; when contested, also try to increase distance to opponent's closest target.
        return (myd + (1 if opp_penalty else 0), cheb(nx, ny, ox, oy))

    best_move, best_val = [0, 0], None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        val = goal_value(nx, ny)
        if best_val is None or val < best_val:
            best_val, best_move = val, [dx, dy]
    return best_move