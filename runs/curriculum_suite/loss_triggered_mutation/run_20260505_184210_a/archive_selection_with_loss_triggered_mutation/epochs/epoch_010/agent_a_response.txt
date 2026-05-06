def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    if not resources: 
        return [0, 0]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def best_cells_for_opponent(k=3):
        scored = []
        for rx, ry in resources:
            d = cheb(ox, oy, rx, ry)
            scored.append((d, rx, ry))
        scored.sort(key=lambda t: (t[0], t[1], t[2]))
        return scored[:k]

    opp_targets = best_cells_for_opponent(3)
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    best_move = [0, 0]
    best_score = -10**18

    cx, cy = (w - 1) / 2, (h - 1) / 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles or not inb(nx, ny):
            continue

        move_score = -10**18
        for opd, rx, ry in opp_targets:
            myd = cheb(nx, ny, rx, ry)
            # Deny: get closer than opponent to their nearest resources
            deny = (opd - myd)
            # Also slightly prefer being near resources (not just denying)
            s = deny * 120 - myd * 3
            # Tighten around center (deterministic tie-break and stability)
            s -= (abs(nx - cx) + abs(ny - cy)) * 0.02
            # If we can "reach" the target now, strongly commit
            if myd == 0:
                s += 500
            # Penalize staying too far behind on all candidate targets
            if s > move_score:
                move_score = s

        if move_score > best_score:
            best_score = move_score
            best_move = [dx, dy]

    return best_move