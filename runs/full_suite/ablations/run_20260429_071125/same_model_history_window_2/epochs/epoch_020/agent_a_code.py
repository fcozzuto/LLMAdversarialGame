def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # Fall back to staying or slight retreat from opponent
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    cur_opp_near = min(cheb(ox, oy, rx, ry) for rx, ry in resources)

    best_move = (0, 0)
    best_value = -10**18
    # Choose next cell that maximizes "winning likelihood" at some resource
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Consider each resource: we prefer smaller (myd - opd), then smaller myd
        best_delta = None
        best_myd = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            delta = myd - opd
            if best_delta is None or delta < best_delta or (delta == best_delta and myd < best_myd):
                best_delta = delta
                best_myd = myd

        # Also try to make opponent farther from their nearest resource after we move
        opp_near_after = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
        # (opponent position unchanged this turn; still deterministic tie-breaker via our target choice)

        # Slight preference for positions that are closer to our selected resource, and for blocking
        value = (-1000 * best_delta) - (10 * best_myd) + (0.01 * (opp_near_after - cur_opp_near))
        # Tie-break: prefer staying if equal, else smallest lex move for determinism
        if value > best_value:
            best_value = value
            best_move = (dx, dy)
        elif value == best_value:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]