def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    # If no visible resources, creep toward center of map to reduce average travel time.
    if not resources:
        tx = (w - 1) // 2
        ty = (h - 1) // 2
        best = [-10**9, 0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            score = -(md(nx, ny, tx, ty))
            if score > best[0]:
                best = [score, dx, dy]
        return [int(best[1]), int(best[2])]

    # Main idea: pick a move that maximizes the best "race" advantage over the opponent
    # (opponent distance minus our distance) toward any resource; tie-break by our closeness.
    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate the best resource from this next position.
        local_best = -10**18
        local_tie = 10**18
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Winning race advantage
            adv = od - sd
            # Prefer getting there sooner, and avoid moves that substantially worsen our distance.
            # Also lightly discourage moves that move away from current best resource by using sd directly.
            score = 1000 * adv - sd
            if score > local_best or (score == local_best and sd < local_tie):
                local_best = score
                local_tie = sd

        # If we're already on a resource (possible if resource present on our tile),
        # take it: higher priority than racing.
        on_res = 1 if (sx, sy) in resources else 0
        if on_res and (nx, ny) == (sx, sy):
            score2 = 10**9 + local_best
        else:
            score2 = local_best

        # Deterministic tie-break: prefer smaller dx, then smaller dy, then staying still.
        if score2 > best_score:
            best_score = score2
            best_move = [dx, dy]
        elif score2 == best_score:
            cand = [dx, dy]
            cur = best_move
            if (abs(cand[0]), abs(cand[1]), cand[0], cand[1], 0 if cand == [0, 0] else 1) < (abs(cur[0]), abs(cur[1]), cur[0], cur[1], 0 if cur == [0, 0] else 1):
                best_move = cand

    return [int(best_move[0]), int(best_move[1])]