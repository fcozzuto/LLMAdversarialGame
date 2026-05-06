def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_score = None
    for tx, ty in resources:
        self_d = cheb((sx, sy), (tx, ty))
        opp_d = cheb((ox, oy), (tx, ty))
        # Prefer resources where we are not slower; strongly penalize being behind.
        # Tie-break by our closeness, then favor central-ish to reduce getting boxed.
        delta = opp_d - self_d
        center = -abs(tx - (w - 1) / 2.0) - abs(ty - (h - 1) / 2.0)
        score = (delta, -self_d, center)
        if best_score is None or score > best_score:
            best_score = score
            best = (tx, ty)
    tx, ty = best

    dx = 1 if tx > sx else (-1 if tx < sx else 0)
    dy = 1 if ty > sy else (-1 if ty < sy else 0)

    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            if mx == 0 and my == 0:
                pass
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                dist = cheb((nx, ny), (tx, ty))
                # Mild preference to move generally toward target; discourage stepping away.
                toward = cheb((sx, sy), (tx, ty)) - dist
                candidates.append((dist, -toward, abs(nx - (sx + dx)) + abs(ny - (sy + dy)), mx, my))
    if not candidates:
        return [0, 0]
    candidates.sort()
    _, _, _, mx, my = candidates[0]
    return [int(mx), int(my)]