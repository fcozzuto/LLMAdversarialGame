def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    if resources:
        # Pre-rank resources by whether we can arrive no later than opponent
        ranked = []
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            ahead = ds - do
            # Prefer we arrive first; then closer; then deterministic tie-break by coordinates
            ranked.append((ahead, ds, rx, ry))
        ranked.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
        # Pick a primary target among those we can plausibly contest; otherwise nearest
        candidates = [t for t in ranked if t[0] <= 0]
        target = candidates[0] if candidates else ranked[0]
        tx, ty = target[2], target[3]
    else:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            nx, ny = sx, sy
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
        # Move value: get closer to target, and avoid stepping onto/near obstacles
        dist_to_target = cheb(nx, ny, tx, ty) if resources else (abs(nx - tx) + abs(ny - ty))
        # Also consider "stealing": resources where opponent is slower
        steal_bonus = 0
        if resources:
            # evaluate up to a few best resources deterministically
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                if ds <= do:
                    # primary reward for minimal ds; slight extra for larger lead
                    steal_bonus = max(steal_bonus, (100 - ds * 5) + (do - ds))
        # Obstacle repulsion
        obs_pen = 0
        for ax, ay in [(nx+1,ny),(nx-1,ny),(nx,ny+1),(nx,ny-1),(nx+1,ny+1),(nx+1,ny-1),(nx-1,ny+1),(nx-1,ny-1)]:
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obstacles:
                obs_pen -= 3
        # Opponent proximity pressure: discourage moving into a cell close to opponent when no resources
        opp_pen = 0
        if resources:
            opp_pen -= cheb(nx, ny, ox, oy) * 0.05
        score = (-dist_to_target * 10) + steal_bonus + obs_pen + opp_pen
        # Deterministic tie-break by move ordering
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]