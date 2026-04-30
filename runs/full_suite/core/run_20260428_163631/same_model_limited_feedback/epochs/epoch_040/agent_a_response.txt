def choose_move(observation):
    x0, y0 = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best, bestv = (0, 0), -10**9
        for dx, dy in moves:
            x, y = x0 + dx, y0 + dy
            if not in_bounds(x, y) or blocked(x, y):
                continue
            v = -dist((x, y), (tx, ty))
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Choose target: prefer resources we are closer to (or can arrive no later),
    # penalize those the opponent can reach sooner; small deterministic tie-break.
    best_targets = []
    for r in resources:
        d_self = dist((x0, y0), r)
        d_opp = dist((ox, oy), r)
        # If blocked by obstacle directly on destination, still allow (engine likely handles pickup on landing)
        # Use score ordering: we want larger advantage and proximity.
        adv = d_opp - d_self
        key = (adv, -d_self, -r[0], -r[1])
        best_targets.append((key, r))
    best_targets.sort(reverse=True)
    _, target = best_targets[0]

    # Move selection: aim to reduce distance to target while avoiding obstacles,
    # and add deterrence if we can contest opponent's path to target.
    best, bestv = (0, 0), -10**9
    for dx, dy in moves:
        x, y = x0 + dx, y0 + dy
        if not in_bounds(x, y) or blocked(x, y):
            continue
        d_new = dist((x, y), target)
        d_opp_new = dist((ox, oy), target)
        # Approximate "opponent pressure": if we're within 1 step of target, boost pickup readiness.
        pressure = 0
        if d_new <= 1:
            pressure += 3.0
        # If we are moving to a cell that increases distance for opponent relative to us, slightly reward.
        # (No true simulation; keep deterministic and simple.)
        my_adv_after = d_opp_new - d_new
        v = 10.0 * my_adv_after - 1.2 * d_new + pressure
        # Slightly avoid moving closer to opponent unless beneficial for contest
        v -= 0.15 * dist((x, y), (ox, oy))
        # Deterministic tie-break
        v += 0.0001 * (x * 0.3 - y * 0.7)
        if v > bestv:
            bestv, best = v, (dx, dy)

    return [int(best[0]), int(best[1])]