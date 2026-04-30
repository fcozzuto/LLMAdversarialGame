def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    sx, sy = self_pos
    ox, oy = opp_pos
    if not resources:
        return [0, 0]

    best = None
    for r in resources:
        rx, ry = r
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        score = (0 if sd <= od else 1, sd - od, sd, rx, ry)  # prefer resources closer/equal; otherwise deny-ish
        if best is None or score < best[0]:
            best = (score, (rx, ry))
    tx, ty = best[1]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            nx, ny = sx + mx, sy + my
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            # prefer moves that reduce distance to target; then reduce distance to opponent (minor blocking)
            cand = (dist((nx, ny), (tx, ty)), dist((nx, ny), (ox, oy)), nx, ny)
            candidates.append((cand, (mx, my)))

    if not candidates:
        return [0, 0]
    candidates.sort()
    mx, my = candidates[0][1]
    return [mx, my]