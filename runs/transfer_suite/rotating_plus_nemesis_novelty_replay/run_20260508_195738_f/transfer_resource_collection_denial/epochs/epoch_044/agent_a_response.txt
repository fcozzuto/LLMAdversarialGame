def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best_target = None
        best_key = None
        for tx, ty in resources:
            sd = abs(tx - sx) + abs(ty - sy)
            od = abs(tx - ox) + abs(ty - oy)
            key = (od - sd, -sd, -(abs(tx - sx) - abs(ty - sy)))
            if best_key is None or key > best_key:
                best_key = key
                best_target = (tx, ty)
        tx, ty = best_target

        best_move = [0, 0]
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            self_to_t = abs(tx - nx) + abs(ty - ny)
            opp_to_t = abs(tx - ox) + abs(ty - oy)
            self_to_opp = abs(nx - ox) + abs(ny - oy)
            opp_to_opp = abs(sx - ox) + abs(sy - oy)
            dist_progress = (abs(tx - sx) + abs(ty - sy)) - self_to_t
            # Encourage moving closer to target and (slightly) away from opponent
            val = (dist_progress, opp_to_t - self_to_t, self_to_opp - opp_to_opp, -self_to_t, -abs(nx - tx) - abs(ny - ty))
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]
        return best_move

    # No resources: move to a safe corner that maximizes distance from opponent
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = None
    best_corner_val = None
    for cx, cy in corners:
        if not inb(cx, cy):
            continue
        val = (abs(cx - ox) + abs(cy - oy), -(abs(cx - sx) + abs(cy - sy)), cx, cy)
        if best_corner_val is None or val > best_corner_val:
            best_corner_val = val
            best_corner = (cx, cy)

    if best_corner is None:
        return [0, 0]

    cx, cy = best_corner
    # Greedy step toward corner, avoiding obstacles; choose best among deltas
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = (abs(nx - ox) + abs(ny - oy), -(abs(nx - cx) + abs(ny - cy)), nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move