def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    reslist = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            reslist.append((int(p[0]), int(p[1])))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def nearest_dist(px, py):
        if not reslist:
            return 10**9
        best = 10**9
        for rx, ry in reslist:
            d = manh(px, py, rx, ry)
            if d < best:
                best = d
        return best

    ox, oy = observation["opponent_position"]
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = -10**30
    self_d0 = nearest_dist(x, y)
    opp_d0 = nearest_dist(ox, oy)

    for dx0, dy0 in deltas:
        nx, ny = x + dx0, y + dy0
        if not inb(nx, ny):
            nx, ny = x, y
        self_d = nearest_dist(nx, ny)
        opp_d = nearest_dist(ox, oy)

        # If we can step onto a resource, prioritize strongly.
        self_gain = (self_d0 - self_d)

        # Opportunistic denial: choose moves that don't let us fall behind opponent.
        # (Approximation: encourage moves that keep advantage over opponent's current distance.)
        advantage = (opp_d - self_d)

        # Slight tie-break: prefer moves toward center to reduce corner-stall in empty pockets.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        center_pref = -manh(nx, ny, cx, cy) * 0.001

        val = self_gain * 1000 + advantage * 10 + center_pref

        if val > best_val:
            best_val = val
            best_move = (dx0, dy0)

    return [int(best_move[0]), int(best_move[1])]