def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Target: prefer resources where we can deny (opp farther than us), then closer to us, then center.
    best = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        denom = 1 + sd
        deny = (od - sd) / denom
        center = -((rx - (w - 1) / 2.0) ** 2 + (ry - (h - 1) / 2.0) ** 2) * 1e-6
        t = (deny, -sd, center, rx, ry)
        if best is None or t > best:
            best = t
    tx, ty = best[3], best[4]

    # Step: choose move that heads toward target while improving denial and avoiding obstacles.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sd2 = md(nx, ny, tx, ty)
        sd_now = md(sx, sy, tx, ty)
        od = md(ox, oy, tx, ty)
        deny_gain = (od - sd2) - (od - sd_now)
        closer = sd2 <= sd_now
        # Prefer reaching target region, then maximizing denial, then minimizing our distance to target.
        score = (10 * deny_gain) + (3 if closer else 0) + (-sd2) + (-md(ox, oy, nx, ny) * 0.01)
        t = (score, -sd2, dx, dy)
        if bestm is None or t > bestm:
            bestm = t
    if bestm is None:
        return [0, 0]
    # Recover dx, dy from tuple
    return [int(bestm[2]), int(bestm[3])]