def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position", [sx, sy]) or [sx, sy]
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    targets = []
    for key in ("resources", "unclaimed_cells"):
        v = observation.get(key, None)
        if isinstance(v, list) and v:
            for p in v:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    targets.append((int(p[0]), int(p[1])))
            if targets:
                break

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        if targets:
            d = min(man(nx, ny, tx, ty) for tx, ty in targets)
            # prefer closer to target, slight preference to move away from opponent if tied
            score = (d, man(nx, ny, ox, oy))
        else:
            # fallback: keep distance from opponent
            score = (-man(nx, ny, ox, oy), 0)
        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]