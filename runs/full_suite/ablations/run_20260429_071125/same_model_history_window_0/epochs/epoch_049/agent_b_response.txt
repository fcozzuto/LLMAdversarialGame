def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx*dx + dy*dy

    def best_target_score(px, py):
        if not resources:
            dc = (px - cx) * (px - cx) + (py - cy) * (py - cy)
            return -dc * 0.001
        best = -10**18
        for rx, ry in resources:
            our_d = dist2((px, py), (rx, ry))
            opp_d = dist2((ox, oy), (rx, ry))
            score = (opp_d - our_d) - 0.05 * our_d
            if score > best:
                best = score
        return best

    best_move = (0, 0)
    best_total = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        target_score = best_target_score(nx, ny)
        opp_sep = dist2((nx, ny), (ox, oy))
        total = target_score + 0.0005 * opp_sep
        if total > best_total:
            best_total = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]