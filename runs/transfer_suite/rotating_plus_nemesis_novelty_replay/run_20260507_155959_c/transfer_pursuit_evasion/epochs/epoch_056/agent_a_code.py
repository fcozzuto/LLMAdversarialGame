def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except Exception:
            pass

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("chaser" in self_role) or (self_role == "pursuer")

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    far_corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = max(far_corners, key=lambda t: abs(t[0] - ox) + abs(t[1] - oy))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best = None
    best_dxdy = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_op = abs(nx - ox) + abs(ny - oy)
        boundary_margin = min(nx, w - 1 - nx, ny, h - 1 - ny)
        center_dist = abs(nx - cx) + abs(ny - cy)

        if is_pursuer:
            # Primary: get closer; Tie: avoid boundary (keep mobility); slight bias against staying still.
            val = (d_op * 1000) + (0 if boundary_margin is None else (100 - boundary_margin)) + (25 if dx == 0 and dy == 0 else 0) + (int(center_dist) % 7)
            better = best is None or val < best
        else:
            # Primary: get farther; Tie: prefer staying away from boundary and heading toward farthest corner.
            goal_dist = abs(best_corner[0] - nx) + abs(best_corner[1] - ny)
            val = (-d_op * 1000) + ((100 - boundary_margin) * 3) + (goal_dist) + (25 if dx == 0 and dy == 0 else 0)
            better = best is None or val > best

        if better:
            best = val
            best_dxdy = [dx, dy]

    return [int(best_dxdy[0]), int(best_dxdy[1])]