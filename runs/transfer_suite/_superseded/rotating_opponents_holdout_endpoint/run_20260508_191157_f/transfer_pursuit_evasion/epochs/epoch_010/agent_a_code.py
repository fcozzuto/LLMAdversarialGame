def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)
    role = (observation.get("self_role") or "pursuer").lower()

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h
    def md(x, y, a, b): return abs(x - a) + abs(y - b)
    def manh_to_op(x, y): return md(x, y, ox, oy)
    def mobility(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obs:
                c += 1
        return c

    # Corner target for evasion to encourage wall-running-like behavior against wall/obstacle tactics
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if w >= 2 and h >= 2:
        # Choose the corner farthest from opponent; deterministic tie-break by fixed order.
        target = max(corners, key=lambda c: (manh_to_op(c[0], c[1]), -c[0], -c[1]))
    else:
        target = (0, 0)

    # If pursuer and can capture by moving onto opponent, do it.
    if role == "pursuer":
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obs and (nx, ny) == (ox, oy):
                return [dx, dy]

    best = None
    best_score = None

    # Heuristic: avoid getting blocked behind obstacles by preferring higher mobility and improving distance (pursuit/evasion).
    # Also bias evader moves toward a corner; pursuer moves toward opponent.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue

        d_now = manh_to_op(nx, ny)
        mob = mobility(nx, ny)

        # Predict opponent response only via symmetry: since deterministic policy of opponent unknown, use only static terms.
        # Extra term: keep moving (avoid stalling) unless stalling is best mobility/distance choice.
        move_pen = 0 if (dx == 0 and dy == 0) else 0.02

        if role == "pursuer":
            # Prefer closer to opponent, then higher mobility to keep chasing options.
            score = (-d_now) * 2.0 + mob * 0.15 - move_pen
        else:
            # Prefer farther from opponent, then mobility, then toward chosen corner.
            d_corner = md(nx, ny, target[0], target[1])
            # Farther from opponent => bigger; closer to corner => smaller d_corner => subtract.
            score = (d_now) * 2.0 + mob * 0.12 - d_corner * 0.25 - move_pen

        # Deterministic tie-break: fixed delta ordering.
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best