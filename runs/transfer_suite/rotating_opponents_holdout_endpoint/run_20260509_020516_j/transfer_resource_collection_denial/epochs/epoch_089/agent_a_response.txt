def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    # Target selection differs from baseline: evaluate candidate moves by "resource race"
    # and add a small tie-breaker for moving away from opponent when race is close.
    opp_pos = (ox, oy)
    best = None
    tr = int(observation.get("turns_remaining", 1) or 1)
    center_bias = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy, nx, ny in moves:
        self_pos2 = (nx, ny)
        my_best = -10**9
        opp_best = -10**9
        # assume optimal opponent targeting resource; compute worst-case advantage
        for res in resources:
            ds = dist(self_pos2, res)
            do = dist(opp_pos, res)
            # Favors grabbing earlier: lower ds, and resources where opponent is farther.
            race = (do - ds) * 10 - ds
            # Encourage not letting opponent also improve race too much
            opp_best = max(opp_best, race)
            my_best = max(my_best, race)
        away = dist(self_pos2, opp_pos)
        cx, cy = center_bias
        cb = -((nx - cx) ** 2 + (ny - cy) ** 2) / (w * h)
        # worst-case-ish: if opponent could choose a resource where advantage is small, penalize
        score = my_best + 0.15 * away + 0.05 * cb + (-0.02 * (tr % 3))
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]