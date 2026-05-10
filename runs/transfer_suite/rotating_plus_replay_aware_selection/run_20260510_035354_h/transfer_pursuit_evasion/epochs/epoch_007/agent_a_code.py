def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs = set((p[0], p[1]) for p in observation.get("obstacles", []))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_is_pursuer = ("purs" in self_role) or (self_role == "pursuer") or ("evad" in opp_role and "purs" in self_role)
    if not self_role:
        self_is_pursuer = False

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_score = None

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Simple obstacle-aware chase/flee: maximize/minimize predicted distance.
    # Prediction: aim 1 step ahead from relative direction (no history needed).
    dxo = ox - sx
    dyo = oy - sy
    step_x = 0 if dxo == 0 else (1 if dxo > 0 else -1)
    step_y = 0 if dyo == 0 else (1 if dyo > 0 else -1)
    px, py = ox + step_x, oy + step_y
    if not (0 <= px < w and 0 <= py < h) or (px, py) in obs:
        px, py = ox, oy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist_now = man(nx, ny, ox, oy)
        dist_pred = man(nx, ny, px, py)

        # Penalty for moving near obstacles to reduce wall-running/funneling.
        neigh_pen = 0
        for ax, ay in ((nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1), (nx + 1, ny + 1), (nx + 1, ny - 1), (nx - 1, ny + 1), (nx - 1, ny - 1)):
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obs:
                neigh_pen += 2

        # Deterministic slight bias to keep moves consistent.
        bias = 0.001 * (abs(dx) + abs(dy)) + 0.00001 * (dx * 3 + dy)

        if self_is_pursuer:
            score = dist_pred + 0.3 * dist_now + neigh_pen + bias
            if best is None or score < best_score:
                best, best_score = [dx, dy], score
        else:
            score = -(dist_pred + 0.3 * dist_now) - 0.2 * neigh_pen - bias
            if best is None or score > best_score:
                best, best_score = [dx, dy], score

    return best if best is not None else [0, 0]