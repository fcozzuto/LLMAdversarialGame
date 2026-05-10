def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "")).lower()
    is_evader = (role == "evader")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def score_move(nx, ny):
        dx, dy = nx - ox, ny - oy
        d2 = dx * dx + dy * dy
        # Prefer moving to safer squares in front of/away from opponent depending on role
        if is_evader:
            # Avoid corners/edges; also avoid moving into obstacles
            edge_pen = (0.5 * (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)))
            center_bonus = (-(abs(nx - cx) + abs(ny - cy)))  # closer to center is better
            return d2 * 10.0 + center_bonus * 2.0 - edge_pen
        else:
            # Pursuer: strong pull toward opponent; break ties by reducing max-sep and centering a bit
            sep_x = abs(nx - ox)
            sep_y = abs(ny - oy)
            cheb = max(sep_x, sep_y)
            # Encourage alignment with opponent direction (diagonal if beneficial)
            align = -abs((nx - sx) - (ox - sx) / (abs(ox - sx) + 1e-9)) - abs((ny - sy) - (oy - sy) / (abs(oy - sy) + 1e-9))
            center_pull = -0.05 * (abs(nx - cx) + abs(ny - cy))
            return -(cheb * 100.0) - d2 * 0.1 + align + center_pull

    best = None
    best_val = None
    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if not inside(nx, ny):
            nx, ny = sx, sy
            dxm, dym = 0, 0
        val = score_move(nx, ny)
        tie = (abs(dxm) + abs(dym), dxm, dym)
        key = (val, -tie[0], -tie[1], -tie[2]) if not is_evader else (val, tie[0], tie[1], tie[2])
        if best_val is None or key > best_val:
            best_val = key
            best = (dxm, dym)

    return [int(best[0]), int(best[1])]