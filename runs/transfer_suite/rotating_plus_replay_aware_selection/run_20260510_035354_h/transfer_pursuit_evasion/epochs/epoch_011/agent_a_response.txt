def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    if "purs" in self_role:
        is_pursuer = True
    elif "evad" in self_role:
        is_pursuer = False
    else:
        is_pursuer = ("purs" in opp_role) and ("evad" not in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score_move(nx, ny):
        dx = nx - ox
        dy = ny - oy
        dist2 = dx * dx + dy * dy
        if is_pursuer:
            return dist2
        else:
            return -dist2

    # Secondary deterministic tiebreak: steer toward (or away from) the farthest corner for evader,
    # and toward the nearest corner for pursuer; also avoid staying if tied.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_pursuer:
        target_corner = min(corners, key=lambda c: (c[0]-sx)**2 + (c[1]-sy)**2)
        prefer = 1.0
    else:
        target_corner = max(corners, key=lambda c: (c[0]-ox)**2 + (c[1]-oy)**2)
        prefer = -1.0

    best_val = None
    best = (0, 0)
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue
        primary = score_move(nx, ny)
        tc = (target_corner[0] - nx)
        td = (target_corner[1] - ny)
        corner_dist2 = tc * tc + td * td
        stay_pen = 0.01 if (dxm == 0 and dym == 0) else 0.0
        # If tied on primary, move that optimizes corner_dist2 and avoids staying.
        val = (primary, corner_dist2 * prefer, stay_pen)
        if best_val is None or val < best_val:
            best_val = val
            best = (dxm, dym)

    return [best[0], best[1]]