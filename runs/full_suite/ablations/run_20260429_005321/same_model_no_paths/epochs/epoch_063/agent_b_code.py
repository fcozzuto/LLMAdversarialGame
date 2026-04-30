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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def sign(t):
        if t > 0: return 1
        if t < 0: return -1
        return 0

    def step_toward(tx, ty):
        cand = []
        dx = sign(tx - sx)
        dy = sign(ty - sy)
        for ddx, ddy in [(dx, dy), (dx, 0), (0, dy), (0, 0)]:
            nx, ny = sx + ddx, sy + ddy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [ddx, ddy]
        return [0, 0]

    if resources:
        best = None
        best_score = None
        for tx, ty in resources:
            d1 = dist(sx, sy, tx, ty)
            d2 = dist(ox, oy, tx, ty)
            score = d1 - d2  # prefer resources where we're not behind
            if best is None or score < best_score or (score == best_score and d1 < best[0]):
                best = (d1, tx, ty)
                best_score = score
        _, tx, ty = best
        return step_toward(tx, ty)

    # No resources: move toward opponent deterministically
    return step_toward(ox, oy)