def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_target():
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            dS = dist(sx, sy, rx, ry)
            dO = dist(ox, oy, rx, ry)
            adv = dO - dS
            if best is None or adv > best[0] or (adv == best[0] and dS < best[1]):
                best = (adv, dS, rx, ry)
        if best is None:
            cx, cy = w // 2, h // 2
            return cx, cy
        return best[2], best[3]

    tx, ty = best_target()

    best_move = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer moves that get closer to target; tie-break by denying opponent (maximize adv after move)
        dS = dist(nx, ny, tx, ty)
        dO = dist(ox, oy, tx, ty)
        score = (dS, -(dO - dS), abs(nx - ox) + abs(ny - oy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]] if best_move else [0, 0]