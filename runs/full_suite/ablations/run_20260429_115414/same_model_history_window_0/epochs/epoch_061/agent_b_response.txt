def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    if not resources:
        best = (0, -10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = dist((nx, ny), (ox, oy))
            if d > best[1]:
                best = (0, d, dx, dy)
        return [best[2], best[3]]

    best_res = None
    best_score = -10**18
    for r in resources:
        ds = dist((sx, sy), r)
        do = dist((ox, oy), r)
        advantage = do - ds
        # Prefer resources we can realistically secure; otherwise deny by maximizing advantage.
        score = (10 * (advantage) - ds) if ds <= do else (5 * advantage - 2 * ds)
        if score > best_score:
            best_score = score
            best_res = r

    tx, ty = best_res[0], best_res[1]
    curd = dist((sx, sy), (tx, ty))

    best = None
    best_tuple = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = dist((nx, ny), (tx, ty))
        # Primary: move closer (or don't worsen). Secondary: maximize distance to opponent to reduce contention.
        delta = nd - curd
        oppd = dist((nx, ny), (ox, oy))
        # Tertiary: deterministic tie-break by preferring diagonal/forward-ish toward target.
        toward = (dx != 0 or dy != 0)
        tup = (delta, -oppd, 0 if toward else 1, dx, dy)
        if best_tuple is None or tup < best_tuple:
            best_tuple = tup
            best = (dx, dy)

    if best is None:
        # All moves blocked; stay.
        return [0, 0]
    return [best[0], best[1]]