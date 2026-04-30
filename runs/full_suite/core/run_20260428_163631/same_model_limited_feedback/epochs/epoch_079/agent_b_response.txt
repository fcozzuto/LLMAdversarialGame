def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    gx = observation.get("grid_width", 8)
    gy = observation.get("grid_height", 8)

    def in_bounds(x, y):
        return 0 <= x < gx and 0 <= y < gy

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev for diagonal moves

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    candidates = [(in_bounds(sx + dx, sy + dy) and (sx + dx, sy + dy) not in obstacles, (dx, dy)) for dx, dy in moves]
    valid = [m for ok, m in candidates if ok]
    if not valid:
        return [0, 0]

    # Choose target where we have the biggest distance advantage over opponent.
    best_target = None
    best_adv = -10**9
    for r in resources:
        adv = dist((ox, oy), r) - dist((sx, sy), r)
        # Prefer resources that are closer when advantage ties.
        key = (adv, -dist((sx, sy), r))
        if key > (best_adv, -10**9):
            best_adv = adv
            best_target = r

    if best_target is None:
        return [0, 0]

    tx, ty = best_target
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        # Heuristic: maximize advantage improvement toward the target, penalize leaving bounds/obstacles already handled.
        self_d = dist((nx, ny), (tx, ty))
        opp_d = dist((ox, oy), (tx, ty))
        adv = opp_d - self_d
        # Also slightly prefer decreasing distance to target.
        val = adv * 100 - self_d * 3
        # Small bias: avoid moving away from the target directionally when possible.
        if dx != 0:
            val += 1 if (tx - sx) * dx > 0 else -1
        if dy != 0:
            val += 1 if (ty - sy) * dy > 0 else -1
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]