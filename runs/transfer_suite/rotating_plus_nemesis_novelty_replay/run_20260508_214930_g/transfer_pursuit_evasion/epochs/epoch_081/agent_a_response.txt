def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = (observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "fugitive"))
    if not is_evader and not any(k in role for k in ("pursuer", "hunter", "seeker")):
        is_evader = False

    obs = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def score_pursuer(nx, ny):
        dx, dy = nx - ox, ny - oy
        return dx * dx + dy * dy  # minimize

    def score_evader(nx, ny):
        dx, dy = nx - ox, ny - oy
        dist = dx * dx + dy * dy  # maximize
        # Mild preference for escaping toward farthest corner from opponent
        best_corner = None
        best_corner_dist = -1
        for cx, cy in corners:
            ddx, ddy = cx - ox, cy - oy
            dcd = ddx * ddx + ddy * ddy
            if dcd > best_corner_dist:
                best_corner_dist = dcd
                best_corner = (cx, cy)
        cx, cy = best_corner
        corner_push = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))  # closer -> higher
        # Combine: maximize dist, also move toward farthest corner
        return dist * 10 + corner_push

    best_move = (0, 0)
    if is_evader:
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            v = score_evader(nx, ny)
            if best_val is None or v > best_val:
                best_val = v
                best_move = (dx, dy)
    else:
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            v = score_pursuer(nx, ny)
            if best_val is None or v < best_val:
                best_val = v
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]