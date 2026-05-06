def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

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

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose a resource where we can contest: opponent is close, and we aren't too far behind.
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        lead = od - sd  # positive => we are closer
        risk = od  # smaller opponent distance => more urgent
        # prioritize: contestability, then urgency; slight tie-break to be closer ourselves
        val = (lead + 0.08) * 30 - risk - 0.001 * (rx + ry)
        if best is None or val > best[0]:
            best = (val, rx, ry, sd, od)
    _, tx, ty, sd_best, od_best = best

    # Predict opponent's next step toward the chosen resource (among valid moves).
    opp_moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = ox + dx, oy + dy
            if valid(nx, ny):
                opp_moves.append((man(nx, ny, tx, ty), dx, dy, nx, ny))
    if opp_moves:
        opp_moves.sort(key=lambda t: (t[0], abs(t[3] - sx) + abs(t[4] - sy), t[1] + 3 * t[2]))
        _, odx, ody, onx, ony = opp_moves[0]
        # Try to deny: move onto opponent's predicted next cell if possible.
        if valid(sx + (onx - sx and (onx > sx) - (onx < sx)) if False else sx, sy):
            # We'll still run normal move scoring below; denial is represented in score.
            pass
    else:
        onx, ony = ox, oy

    # Move scoring: (1) avoid obstacles, (2) deny by approaching predicted opponent-next cell,
    # (3) also progress toward target resource if denial isn't reachable.
    best_move = [0, 0]
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # Immediate denial preference
            deny = man(nx, ny, onx, ony)
            # Progress to resource
            prog = man(nx, ny, tx, ty)
            # If we're already close to target, favor finishing it
            finish_bias = -2.0 * (1 if prog == 0 else 0) - 0.2 * (1 if prog <= 1 else 0)
            # Also avoid moving away from target when we are within same reach tier
            tier = 1 if sd_best <= od_best else -1
            away_pen = 0.3 * tier * (prog - sd_best)
            score = -2.2 * deny - 0.9 * prog + finish_bias - away_pen
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
    return best_move