def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = {tuple(p) for p in observation.get("obstacles", [])}
    resources = [tuple(p) for p in observation.get("resources", [])]
    self_name = observation.get("self_name", "")
    opponent_name = observation.get("opponent_name", "")

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a target resource: prefer close to self, penalize if opponent is much closer.
    best = None
    for r in resources:
        ds = dist((sx, sy), r)
        do = dist((ox, oy), r)
        score = ds - (0.6 * do)
        # Deterministic tie-breakers
        key = (score, ds, r[0], r[1])
        if best is None or key < best[0]:
            best = (key, r)
    target = best[1] if best else (w // 2, h // 2)

    # Candidate moves: stay or move one step (including diagonals), avoiding obstacles/bounds.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # Pick move that decreases distance to target; also consider not giving opponent advantage.
    best_move = None
    for dx, dy, nx, ny in candidates:
        myd = dist((nx, ny), target)
        opd = dist((ox, oy), target)
        # Prefer moves that keep opponent not closer than us (softly), and avoid moving into "hot" zones.
        opp_adv = max(0, opd - myd)
        opp_dist_to_me = dist((ox, oy), (nx, ny))
        # Deterministic preference order within ties.
        key = (myd, -opp_adv, -opp_dist_to_me, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)

    return [int(best_move[1]), int(best_move[2])]