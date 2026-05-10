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

    # Target guidance: evader goes to farthest corner from opponent; pursuer chases opponent.
    if is_evader:
        tx, ty = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
        primary_sign = 1  # maximize distance from opponent
    else:
        tx, ty = ox, oy
        primary_sign = -1 # minimize distance to opponent

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid_pos(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        d_tgt = dist2(nx, ny, tx, ty)

        # Local survivability: prefer moves that keep more neighboring options open.
        blocked = 0
        for ax, ay in moves:
            px, py = nx + ax, ny + ay
            if not valid_pos(px, py):
                blocked += 1

        # Tie-breakers: prefer staying off obstacles trivially handled, also prefer progress toward target.
        score = primary_sign * d_opp + (-0.05) * blocked + (-0.001) * d_tgt
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move