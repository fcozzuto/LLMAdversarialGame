def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs_set = {(p[0], p[1]) for p in obstacles}

    self_role = (observation.get("self_role") or "").lower()
    is_evader = ("evad" in self_role) or ("runner" in self_role) or ("escape" in self_role)
    is_pursuer = ("purs" in self_role) or ("seeker" in self_role)
    if not (is_evader or is_pursuer):
        is_pursuer = True

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid_pos(x, y):
        return in_bounds(x, y) and (x, y) not in obs_set

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx*dx + dy*dy

    tx, ty = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy)) if is_evader else (ox, oy)

    best = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid_pos(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        d_tgt = dist2(nx, ny, tx, ty)

        # Obstacle pressure: prefer being less "boxed in" by immediate blocked neighbors.
        blocked_nei = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if (ax, ay) != (nx, ny) and (not in_bounds(ax, ay) or (ax, ay) in obs_set):
                blocked_nei += 1

        # Deterministic evaluation.
        if is_evader:
            score = 3*d_opp - 1*d_tgt - 0.2*blocked_nei
        else:
            score = 3*(-d_opp) - 1*d_tgt - 0.2*blocked_nei

        if best_score is None or score > best_score or (score == best_score and [dx, dy] < best):
            best_score = score
            best = [dx, dy]

    # Fallback (shouldn't trigger often).
    if best_score is None:
        return [0, 0]
    return best