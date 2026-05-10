def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # deterministic ordering
    resources = sorted((int(x), int(y)) for x, y in resources)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Immediate collect if moving onto a resource
        imm = 0.0
        for rx, ry in resources:
            if nx == rx and ny == ry:
                imm = 5.0
                break

        # Choose best target by 1-step advantage against opponent
        local_best = -10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # prefer targets we can reach sooner; if equal, prefer those we are closer to now (anti-denier)
            adv = (opd - myd)
            # mild center preference to break ties
            center = -(abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)) * 0.01
            # prefer targets closer in absolute time to reduce wandering
            time_pref = -(myd * 0.05)
            # prefer "safer" targets not immediately adjacent to opponent's ability to snatch
            snap_pen = 0.0 if myd <= opd else -(myd - opd) * 0.1
            val = adv + center + time_pref + snap_pen
            if val > local_best:
                local_best = val

        score = imm + local_best
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]