def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = {(a, b) for a, b in obstacles}
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h
    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return (dx*dx + dy*dy) ** 0.5
    def best_target_value(sx, sy):
        if not resources:
            cx, cy = (w - 1) / 2, (h - 1) / 2
            return -dist(sx, sy, cx, cy)
        best = -1e18
        for rx, ry in resources:
            sd = dist(sx, sy, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Prefer resources we can reach at least as well as opponent (od - sd positive),
            # and also prefer being close even when both can.
            gain = (od - sd)
            closeness = -0.15 * sd
            # If resource is on our current square, ensure strong pull to it.
            on_bonus = 6.0 if (sx == rx and sy == ry) else 0.0
            val = gain + closeness + on_bonus
            if val > best:
                best = val
        return best
    # If we are stuck on obstacle (unlikely), move toward nearest in-bounds cell.
    if (x, y) in obs_set:
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obs_set:
                return [dx, dy]
        return [0, 0]
    best_move = (0, 0)
    best_score = -1e18
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            score = -1e9
        else:
            # Penalize obstacle squares strongly.
            obs_pen = 8.0 if (nx, ny) in obs_set else 0.0
            # Encourage slight spread away from opponent while still targeting.
            opp_d = dist(nx, ny, ox, oy)
            safety = 0.02 * opp_d
            score = best_target_value(nx, ny) + safety - obs_pen
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]