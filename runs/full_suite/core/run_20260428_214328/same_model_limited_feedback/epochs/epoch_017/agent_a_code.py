def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick target resource with maximal advantage for us, then nearest tie-break
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d1 = dist((sx, sy), (rx, ry))
        d2 = dist((ox, oy), (rx, ry))
        adv = d2 - d1
        key = (-adv, d1, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    if best is None:
        # No resources: move to safer direction toward center
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best_mv = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = abs(nx - tx) + abs(ny - ty)
            if sc < best_mv[0]:
                best_mv = (sc, dx, dy)
        return [int(best_mv[1]), int(best_mv[2])]

    tx, ty = best[1]
    # Greedy step toward target, with deterministic obstacle-avoidance and evaluation
    pref_dx = 0 if tx == sx else (1 if tx > sx else -1)
    pref_dy = 0 if ty == sy else (1 if ty > sy else -1)

    best_mv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Prefer moving closer to target; discourage giving opponent closer access
        d_self = dist((nx, ny), (tx, ty))
        d_opp = dist((ox, oy), (tx, ty))
        # Bonus if we land on resource
        on_res = 1 if (nx, ny) == (tx, ty) else 0
        # Small preference for axis/diag alignment toward target
        align = 0 if (dx == pref_dx and dy == pref_dy) else 1
        # Deterministic scoring: primary closer, then higher advantage, then alignment
        score = (-on_res, d_self, -(d_opp - d_self), align, dx, dy)
        if best_mv is None or score < best_mv[0]:
            best_mv = (score, dx, dy)

    if best_mv is None:
        return [0, 0]
    return [int(best_mv[1]), int(best_mv[2])]