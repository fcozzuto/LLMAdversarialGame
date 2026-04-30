def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    center = (w // 2, h // 2)

    best_move = (0, 0)
    best_score = -10**18

    dres_now = min((cheb(sx, sy, rx, ry) for rx, ry in resources), default=10**9)
    dopp_now = cheb(sx, sy, ox, oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        dopp = cheb(nx, ny, ox, oy)
        dres = min((cheb(nx, ny, rx, ry) for rx, ry in resources), default=10**9)

        # Prefer reducing resource distance; also keep some spacing from opponent.
        score = 0.0
        if resources:
            score += (dres_now - dres) * 4.0
            score += -dres * 0.8
            # If we can become strictly closer than opponent to some resource, reward.
            score += (max(0.0, dres_now - dres) / (1.0 + dres)) * 2.0

            # Consider "contested" resources: where we can beat opponent by moving closer.
            # Lightweight: compare nearest resource distances for us vs opponent after move.
            opp_nearest = min((cheb(ox, oy, rx, ry) for rx, ry in resources), default=10**9)
            if dres < opp_nearest:
                score += 3.0
        else:
            score += -cheb(nx, ny, center[0], center[1]) * 0.5

        # Avoid moving adjacent/too close to opponent unless it also helps resource capture.
        score += (dopp - dopp_now) * 0.6
        if dopp <= 1:
            score -= 3.5
        if dx == 0 and dy == 0:
            score -= 0.2

        # Deterministic tie-break: prefer smaller |dx|+|dy| then lexicographic.
        tie_key = (abs(dx) + abs(dy), dx, dy)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)
            best_tie = tie_key
        elif score == best_score:
            if tie_key < best_tie:
                best_move = (dx, dy)
                best_tie = tie_key

    return [int(best_move[0]), int(best_move[1])]