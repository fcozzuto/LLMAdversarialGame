def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev for king-moves

    # pick resource where we have advantage over opponent
    best = None
    best_score = None
    for rx, ry in resources:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Prefer closer-by advantage; deterministic tie-break by resource position
        score = (od - sd) * 10 - sd
        key = (score, -rx, -ry)
        if best is None or key > best_score:
            best = (rx, ry)
            best_score = key

    tx, ty = best
    steps = []
    # order directions deterministically: prioritize dx then dy with move toward target
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                steps.append((0, 0))
            else:
                steps.append((dx, dy))
    # deterministic scoring for candidate moves
    candidates = []
    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # avoid head-on: if we can move to same cell (opponent), penalize
        d_self = dist((nx, ny), (tx, ty))
        d_opp_to_target = dist((ox, oy), (tx, ty))
        # if we are no longer advantaged, slight penalty to encourage changing target
        sd_now = dist((nx, ny), (tx, ty))
        advantage = (d_opp_to_target - sd_now)
        # safety: if opponent is very close, prefer to increase distance
        d_opp = dist((nx, ny), (ox, oy))
        score = (-d_self * 3) + (advantage * 2) + (d_opp * 0.5)
        if (nx, ny) == (ox, oy):
            score -= 100
        # tie-breakers
        candidates.append((score, dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    candidates.sort(reverse=True)
    _, dx, dy, _, _ = candidates[0]
    return [int(dx), int(dy)]