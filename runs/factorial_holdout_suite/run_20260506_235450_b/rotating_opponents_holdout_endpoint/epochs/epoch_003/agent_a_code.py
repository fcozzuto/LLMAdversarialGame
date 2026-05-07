def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = set((x, y) for x, y in obstacles)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    # Target bias: prefer resources where we are closer in Manhattan distance,
    # and also prefer cells that are on the "far side" of the opponent (harder to contest for sweeps).
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        self_d = manh(sx, sy, rx, ry)
        opp_d = manh(ox, oy, rx, ry)
        # Far-side bias relative to opponent cornering direction
        bx = 1 if rx - ox >= 0 else 0
        by = 1 if ry - oy >= 0 else 0
        far_bias = (abs(rx - ox) + abs(ry - oy))  # larger => more "separated"
        key = (-(opp_d - self_d), self_d, -(far_bias + (bx + by)), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best if best is not None else (sx, sy)

    # Choose one step that increases our advantage while making the chosen target more reachable.
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        self_d2 = manh(nx, ny, tx, ty)
        opp_d2 = manh(ox, oy, tx, ty)
        # Advantage after move + avoid getting too close to opponent for tie situations.
        val = (opp_d2 - self_d2, -self_d2, -(abs(nx - ox) + abs(ny - oy)), nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move if best_val is not None else [0, 0]