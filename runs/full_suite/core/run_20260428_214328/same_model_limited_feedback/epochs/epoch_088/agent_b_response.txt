def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev for king moves

    # If no resources, drift to reduce distance to opponent's corner-ish
    if not resources:
        tx = 0 if ox > (w - 1) / 2 else (w - 1)
        ty = 0 if oy > (h - 1) / 2 else (h - 1)
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    # Pick best resource: prefer closer to self, slightly discourage resources opponent can reach sooner
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        key = (ds - 0.35 * do, ds, (rx + ry) % 2)  # deterministic tie-breaker
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    options = []
    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Evaluate move by resulting objective to target, plus avoid moving away when tied
        ds2 = dist((nx, ny), (tx, ty))
        do2 = dist((ox, oy), (tx, ty))
        key = (ds2 - 0.35 * do2, ds2, abs(nx - ox) + abs(ny - oy), dx, dy)
        options.append((key, [dx, dy]))

    # Always have at least stay if valid; else fallback to [0,0]
    if not options:
        return [0, 0]
    options.sort(key=lambda x: x[0])
    return options[0][1]