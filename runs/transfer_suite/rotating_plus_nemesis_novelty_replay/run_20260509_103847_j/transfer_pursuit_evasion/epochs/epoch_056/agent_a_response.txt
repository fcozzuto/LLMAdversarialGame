def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = observation.get("obstacles") or []
    obs_set = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    sr = (observation.get("self_role") or "").lower()
    pr = (observation.get("opponent_role") or "").lower()
    self_evader = ("evader" in sr) or ("evade" in sr) or ("escape" in sr)
    opp_pursuer = ("purs" in pr) or ("chaser" in pr) or ("catch" in pr) or ("hunt" in pr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-break order: prefer keeping still, then x-advance, then y-advance
    tie_pref = {(0, 0): 0, (1, 0): 1, (-1, 0): 1, (0, 1): 1, (0, -1): 1,
                 (1, 1): 2, (1, -1): 2, (-1, 1): 2, (-1, -1): 2}

    # Use different weights depending on role to avoid oscillation near capture (capture_radius=0)
    best_move = [0, 0]
    if not self_evader:
        # Pursuer: minimize squared distance; add mild preference to avoid moving toward edges too early
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            ddx, ddy = nx - ox, ny - oy
            d2 = ddx * ddx + ddy * ddy
            edge_pen = (nx == 0 or nx == w - 1) + (ny == 0 or ny == h - 1)
            val = d2 + 0.05 * edge_pen
            if best_val is None or val < best_val or (val == best_val and tie_pref[(dx, dy)] < tie_pref[tuple(best_move)]):
                best_val = val
                best_move = [dx, dy]
    else:
        # Evader: maximize squared distance; also bias toward a corner opposite the pursuer
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        # choose farthest corner from opponent deterministically
        far_corner = corners[0]
        far_d2 = None
        for c in corners:
            cx, cy = c
            ddx, ddy = cx - ox, cy - oy
            d2 = ddx * ddx + ddy * ddy
            if far_d2 is None or d2 > far_d2 or (d2 == far_d2 and (cx, cy) > far_corner):
                far_d2 = d2
                far_corner = c
        cx, cy = far_corner

        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            ddx, ddy = nx - ox, ny - oy
            d2 = ddx * ddx + ddy * ddy
            # Prefer moving toward the chosen corner while staying far from opponent
            to_corner = (cx - nx) * (cx - nx) + (cy - ny) * (cy - ny)
            # If opponent is very close, prioritize distance increase over corner-seeking
            opp_d2 = (ox - sx) * (ox - sx) + (oy - sy) * (oy - sy)
            corner_w = 0.2 if opp_d2 < 9 else 0.5
            val = -(d2) + corner_w * to_corner
            if best_val is None or val < best_val or (val == best_val and tie_pref[(dx, dy)] < tie_pref[tuple(best_move)]):
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]