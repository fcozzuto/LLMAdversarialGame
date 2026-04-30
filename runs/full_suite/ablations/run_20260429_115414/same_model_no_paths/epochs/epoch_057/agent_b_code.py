def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if resources:
        opp_best = []
        for rx, ry in resources:
            opp_best.append((cheb(ox, oy, rx, ry), rx, ry))
        opp_best.sort()
        top = opp_best[:4]  # keep deterministic and small

        best_score = -10**9
        best_move = (0, 0)

        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue

            score = 0
            min_my = 10**9
            min_op = 10**9
            for _, rx, ry in top:
                d_my = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                if d_my < min_my:
                    min_my = d_my
                if d_op < min_op:
                    min_op = d_op
                # Prefer positions that beat opponent's distance to a valuable resource
                score = max(score, (min_op - d_my) * 10 - d_my)

            # If we can reach a resource this turn, prioritize
            score += -min_my
            # Tie-breaker: deterministic by coordinates
            score += -((nx * 31 + ny) % 997) * 1e-6

            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No visible resources: head toward an unblocked corner/edge point in a deterministic way
    candidates = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, h // 2)]
    candidates.sort(key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[1], p[0]))
    target = candidates[0]
    tx, ty = target

    best_d = 10**9
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        if d < best_d or (d == best_d and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_d = d
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]