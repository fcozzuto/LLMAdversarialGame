def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    target = None
    if resources:
        bestd = None
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if bestd is None or d < bestd or (d == bestd and (rx < (target[0] if target else 10**9) or ry < (target[1] if target else 10**9))):
                bestd = d
                target = (rx, ry)
    else:
        target = (w // 2, h // 2)

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist_to_res = cheb(nx, ny, target[0], target[1]) if resources else cheb(nx, ny, target[0], target[1])
        dist_to_opp = cheb(nx, ny, ox, oy)

        # Prefer taking a resource immediately.
        takes = 1 if resources and (nx, ny) in set(resources) else 0

        # Deterministic tie-break: higher is better score.
        score = (takes * 10_000) + (-(dist_to_res * 10)) + (dist_to_opp)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # Tie-break deterministically by a fixed order of moves.
            order = {d: i for i, d in enumerate(deltas)}
            if order[(dx, dy)] < order[best_move]:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]