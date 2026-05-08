def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        best = None
        bestm = [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            val = man(nx, ny, ox, oy)
            if best is None or val < best or (val == best and (nx, ny) < (sx + bestm[0], sy + bestm[1])):
                best = val
                bestm = [dx, dy]
        return bestm

    best_score = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        local_best = None
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)

            # Advantage-first, then speed. Strongly avoid ceding resources.
            # Scores are deterministic integers.
            adv = do - ds  # positive means we are closer
            score = 6 * adv - 2 * ds + (2 if ds == 0 else 0) - (3 if adv < 0 and do <= ds + 1 else 0)

            # Prefer resources opponent can reach soon less than ours (force earlier grabs/intercepts).
            if do < ds:
                score += 2

            if local_best is None or score > local_best:
                local_best = score

        if best_score is None or local_best > best_score or (local_best == best_score and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_score = local_best
            best_move = [dx, dy]

    return best_move