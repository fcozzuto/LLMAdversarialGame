def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_pursuer = ("purs" in self_role) or ("chase" in self_role)
    if ("purs" not in self_role) and ("evad" not in self_role) and ("purs" in opp_role):
        is_pursuer = False

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1,  0), (0,  0), (1,  0),
             (-1,  1), (0, 1), (1, 1)]
    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Prefer staying mobile near obstacles: penalize moving into tight corners.
    def tight(nx, ny):
        cnt = 0
        for dx, dy in moves:
            tx, ty = nx + dx, ny + dy
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                cnt += 1
        return cnt

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inside(nx, ny):
            continue
        vdx, vdy = ox - nx, oy - ny
        dist2 = vdx * vdx + vdy * vdy

        # Line-of-approach bias to reduce kiting around walls: encourage decreasing
        # distance and also approaching along dominant axis.
        if abs(vdx) >= abs(vdy):
            align = (1 if (ox >= nx and dx != -1) or (ox < nx and dx != 1) else 0)
        else:
            align = (1 if (oy >= ny and dy != -1) or (oy < ny and dy != 1) else 0)

        # Scoring: pursuer minimizes dist; evader maximizes dist.
        # Add obstacle tightness penalty for pursuer (and reward for evader).
        val = (-dist2 if is_pursuer else dist2) + (2.0 * align if is_pursuer else -2.0 * align)
        val += (-0.6 * tight(nx, ny) if is_pursuer else 0.6 * tight(nx, ny))

        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]