def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        best = None
        best_key = None
        for r in resources:
            ourd = dist((sx, sy), r)
            oppd = dist((ox, oy), r)
            key = (oppd - ourd, -ourd, r[1], r[0])  # prioritize winning race; deterministic tie-break
            if best is None or key > best_key:
                best = r
                best_key = key
        tx, ty = best
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        cand = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)]
        for ddx, ddy in cand:
            nx, ny = sx + ddx, sy + ddy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [ddx, ddy]

    # Fallback: move away from opponent if no resources or blocked
    dx = 0 if sx == ox else (1 if sx < ox else -1)
    dy = 0 if sy == oy else (1 if sy < oy else -1)
    cand = [(-dx, -dy), (-dx, 0), (0, -dy), (0, 0)]
    for ddx, ddy in cand:
        nx, ny = sx + ddx, sy + ddy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [ddx, ddy]

    return [0, 0]