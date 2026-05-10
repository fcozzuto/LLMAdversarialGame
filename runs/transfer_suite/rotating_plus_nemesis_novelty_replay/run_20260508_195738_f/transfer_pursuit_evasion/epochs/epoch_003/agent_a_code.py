def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_pursuer = ("purs" in self_role) or ("chase" in self_role) or ("tag" in self_role)
    if ("purs" not in self_role) and ("evad" not in self_role) and (("purs" in opp_role) or ("chase" in opp_role) or ("tag" in opp_role)):
        is_pursuer = False

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1,  0), (0,  0), (1,  0),
             (-1,  1), (0,  1), (1,  1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def tight(nx, ny):
        t = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                t += 1
        return t

    def edge_bias(nx, ny):
        return max(nx, w - 1 - nx) + max(ny, h - 1 - ny)

    dist2_curr = (ox - x) * (ox - x) + (oy - y) * (oy - y)
    best_move = (0, 0)
    best_val = None

    # Deterministic iteration order: already fixed in moves list.
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inside(nx, ny):
            continue
        vdx, vdy = ox - nx, oy - ny
        dist2_new = vdx * vdx + vdy * vdy
        t = tight(nx, ny)

        if is_pursuer:
            # Lower is better: prioritize smaller distance, then break ties by advancing and keeping mobility.
            progress = dist2_curr - dist2_new
            val = dist2_new * 1000 - progress * 50 + t * 30 + (edge_bias(nx, ny) * 2)
            better = (best_val is None) or (val < best_val)
        else:
            # Evader: maximize distance, prefer moving toward edges/corners away from pursuer, avoid tight spots.
            progress = dist2_new - dist2_curr
            val = -(dist2_new * 1000 + progress * 80) - edge_bias(nx, ny) * 3 + t * 50
            better = (best_val is None) or (val > best_val)

        if better:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]