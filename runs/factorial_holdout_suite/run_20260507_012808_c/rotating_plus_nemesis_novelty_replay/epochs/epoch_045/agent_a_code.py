def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick best target resource: closest to us, farther from opponent.
    if resources:
        best = None
        for rx, ry in resources:
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Minimization: lower is better. Favor grabbing earlier and denying opponent.
            score = ds - 0.35 * do + 0.001 * (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2))
            if best is None or score < best[0]:
                best = (score, rx, ry)
        _, tx, ty = best
    else:
        # No visible resources: drift to opponent-far corner while avoiding obstacles.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            if (cx, cy) in obstacles:
                continue
            score = dist(sx, sy, cx, cy) - 0.25 * dist(ox, oy, cx, cy)
            if best is None or score < best[0]:
                best = (score, cx, cy)
        if best is None:
            return [0, 0]
        _, tx, ty = best

    # Choose one-step move maximizing progress to target, tie-breaking by safety and opponent distance.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    bestv = None
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if not in_bounds(nx, ny):
            continue
        v_self = dist(nx, ny, tx, ty)
        v_op = dist(nx, ny, ox, oy)
        # Prefer smaller v_self; break ties by larger v_op (deny opponent), then prefer staying (deterministic).
        val = (v_self, -v_op, abs(dx) + abs(dy))
        if bestv is None or val < bestv:
            bestv = val
            bestm = (dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]