def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or ("evader" in opponent_role and "pursuer" not in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def mobility(x, y):
        m = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                m += 1
        return m

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if nx == ox and ny == oy:
            return [dx, dy]

        d = dist2(nx, ny)
        mob = mobility(nx, ny)

        # Secondary preference for evader: move toward the farthest corner
        if is_evader:
            far_corner = max(dist2(cx, cy) for (cx, cy) in corners)
            corner_bias = max(dist2(nx, ny) - (far_corner * 0.0), 0.0)  # keeps deterministic, lightweight
            val = (d, mob, corner_bias, -nx, -ny)
        else:
            # Pursuer: strongly reduce distance; then increase mobility
            val = (-d, mob, nx, ny)

        if best is None or val > best_val:
            best = [dx, dy]
            best_val = val

    if best is None:
        return [0, 0]
    return best