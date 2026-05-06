def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick target that opponent is relatively far from (anti-chase).
    best_t = None
    best_key = None
    for t in resources:
        sd = man((sx, sy), t)
        od = man((ox, oy), t)
        key = (od - sd, -sd, t[0], t[1])
        if best_key is None or key > best_key:
            best_key, best_t = key, t

    tx, ty = best_t
    # If already on a resource, stay to secure it.
    if (sx, sy) == (tx, ty):
        return [0, 0]

    # Score each move: approach target, keep anti-chase advantage, avoid opponent pressure.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        sd2 = man((nx, ny), (tx, ty))
        od2 = man((ox, oy), (tx, ty))
        adv = od2 - sd2  # want large advantage

        # Pressure: don't move adjacent to opponent unless it greatly helps target approach.
        opp_dist = max(0, man((nx, ny), (ox, oy)) - 1)
        pressure_penalty = -1.5 / (opp_dist + 1.0)

        # Tie-breakers: keep options toward more distant resources.
        key2 = (adv, -sd2, -abs(nx - tx) - abs(ny - ty), -dx, -dy, nx, ny)
        score = (adv * 10.0) - sd2 + pressure_penalty

        if best_score is None or score > best_score or (score == best_score and key2 > best_key):
            best_score = score
            best_key = key2
            best_move = [dx, dy]

    return best_move