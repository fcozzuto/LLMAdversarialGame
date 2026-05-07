def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose a target where we can get there first; otherwise, deny by moving where we reduce their lead.
    best = None
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        lead = d_opp - d_self  # positive => we are closer
        # Prefer guaranteed-ish leads; if not, minimize opponent advantage and distance.
        key = (lead, -d_self, -d_opp, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Greedy step toward target; break ties by keeping away from opponent and avoiding obstacles.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            ds = cheb(nx, ny, tx, ty)
            do = cheb(nx, ny, ox, oy)
            # Primary: decrease distance to target; Secondary: increase distance from opponent (shadow); Tertiary: move ordering deterministically.
            score = ( -ds, do, -abs(dx), -abs(dy), dx, dy )
            moves.append((score, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: t[0], reverse=False)
    # moves[0] has smallest score tuple; adjust: we used negatives, so minimize works for -ds; keep deterministic by stable sort.
    return [moves[0][1], moves[0][2]]