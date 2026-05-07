def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev (diagonal allowed)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    my = (sx, sy)
    opp = (ox, oy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        for r in resources:
            r = tuple(r)
            if r in obstacles:
                continue
            md = dist(my, r)
            od = dist(opp, r)
            # Prioritize resources we can reach not later than opponent; otherwise deny by being closer.
            score = md - od * 0.95
            if best is None or score < best[0] or (score == best[0] and md < best[1]):
                best = (score, md, od, r)
        target = best[3]
    else:
        target = None

    if target is None:
        return [0, 0]

    tx, ty = target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Candidate preferred step: direct toward target; otherwise choose best legal alternative.
    candidates = []
    pref = (dx, dy)
    for mdx, mdy in [pref] + [m for m in moves if m != pref]:
        nx, ny = sx + mdx, sy + mdy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((mdx, mdy, dist((nx, ny), target)))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (t[2], abs(t[0]) + abs(t[1]), t[0], t[1]))
    return [int(candidates[0][0]), int(candidates[0][1])]