def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    seen = set()
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))
    if not resources:
        return [0, 0]

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        adx = dx if dx >= 0 else -dx
        ady = dy if dy >= 0 else -dy
        return adx if adx > ady else ady

    # Choose a target resource where we most likely get there first.
    best = None
    best_score = -10**18
    for rx, ry in resources:
        md = kdist(sx, sy, rx, ry)
        od = kdist(ox, oy, rx, ry)
        # Prefer big distance advantage; break ties by closer to us.
        score = (od - md) * 1000 - md
        if score > best_score:
            best_score = score
            best = (rx, ry)

    rx, ry = best

    # Among legal moves, pick one that maximizes our priority (reach first) and minimizes our distance.
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        myd = kdist(nx, ny, rx, ry)
        opd = kdist(ox, oy, rx, ry)
        val = (opd - myd) * 1000 - myd
        # Small deterministic bias to avoid oscillation: prefer not moving backwards in x then y.
        val -= (dx < 0) * 0.1
        val -= (dy < 0) * 0.01
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]