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

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Choose target that maximizes our advantage over opponent; deterministic tie-break.
    best = None
    best_key = None
    for rx, ry in resources:
        d_us = man(sx, sy, rx, ry)
        d_opp = man(ox, oy, rx, ry)
        score_adv = d_opp - d_us  # higher means we are closer
        # discourage moving to near-opponent row band to reduce race losses
        row_band_pen = 0
        if abs(oy - sy) <= 1 and abs(ry - oy) <= 1:
            row_band_pen = 3
        # slight preference for closer resources once advantage is similar
        key = (score_adv - row_band_pen, -d_us, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Greedy step toward target; if blocked, try alternatives deterministically.
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            new_dist = man(nx, ny, tx, ty)
            # If moving makes us closer to target while reducing opponent's access, prefer.
            opp_dist_after = man(ox, oy, tx, ty)
            candidates.append(((new_dist, -abs((ox - nx)) - abs((oy - ny)), dx, dy), (dx, dy)))
    candidates.sort(key=lambda t: t[0])
    return list(candidates[0][1]) if candidates else [0, 0]