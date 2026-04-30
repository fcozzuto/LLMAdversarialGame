def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    maxd = max(w, h)

    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    candidates = []
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        score = (do - ds) * 1000 - ds  # prefer resources opponent is less able to take
        candidates.append((score, ds, rx, ry))
    if candidates:
        candidates.sort(reverse=True)
        _, _, tx, ty = candidates[0]
    else:
        tx, ty = (w//2, h//2)

    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            d = dist((nx, ny), (tx, ty))
            d_opp = dist((nx, ny), (ox, oy))
            v = -d * 10 + d_opp * 0.01  # small repulsion from opponent when tied
            if best is None or v > best[0]:
                best = (v, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]