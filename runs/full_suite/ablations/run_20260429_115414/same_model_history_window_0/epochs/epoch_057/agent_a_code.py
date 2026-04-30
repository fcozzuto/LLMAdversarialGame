def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev for 8-dir

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)] + [(0, 0)]

    # Pick resource where we have best distance advantage (my_dist - opp_dist minimal).
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = dist((sx, sy), (rx, ry))
        opd = dist((ox, oy), (rx, ry))
        # Small tie-breakers for determinism: prefer farther away if equal my advantage (to reduce contention), then lower myd.
        score = (myd - opd, -myd, myd, abs(sx - rx) + abs(sy - ry))
        if best is None or score < best[0]:
            best = (score, (rx, ry))
    if best is None:
        # No resources: drift toward center while avoiding obstacles.
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best[1]

    # Choose best legal step that decreases distance to target; prefer moves that also increase opponent distance.
    opp_future_best = None
    my_future_best = None
    chosen = (0, 0)
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        myd2 = dist((nx, ny), (tx, ty))
        opd2 = dist((ox, oy), (tx, ty))
        # Also consider "blocking": if next step moves closer to opponent's current pos, avoid; if it moves away, prefer.
        block = dist((nx, ny), (ox, oy))
        # Key: primary reduce distance to target, then maximize distance from opponent, then deterministic tiebreak.
        key = (myd2, -block, abs(dx) + abs(dy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]