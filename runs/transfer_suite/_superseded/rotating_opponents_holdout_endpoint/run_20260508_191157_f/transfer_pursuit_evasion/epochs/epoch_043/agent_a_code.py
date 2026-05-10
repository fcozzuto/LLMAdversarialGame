def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    role = observation.get("self_role", "pursuer")
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # If possible, capture immediately (role likely "pursuer")
    if role == "pursuer":
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny) and nx == ox and ny == oy:
                return [dx, dy]

    # Targeting for both roles
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # For evader, bias toward farthest corner from pursuer; for pursuer, bias toward opponent and center
    if role == "evader":
        tx, ty = max(corners, key=lambda c: manh(c[0], c[1], ox, oy))
        want = "far"
    else:
        tx, ty = (ox, oy)
        want = "near"

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_opp = manh(nx, ny, ox, oy)
        d_tgt = manh(nx, ny, tx, ty)

        # Penalize getting closer to obstacles? Instead, lightly prefer higher "free" moves.
        free = 0
        for ex, ey in deltas:
            px, py = nx + ex, ny + ey
            if ok(px, py):
                free += 1

        if want == "near":
            score = (-d_opp, d_tgt, -free, dx, dy)
        else:
            # prioritize increasing distance to opponent; then maximize progress toward chosen corner
            score = (d_opp, -d_tgt, free, -dx, -dy)

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]