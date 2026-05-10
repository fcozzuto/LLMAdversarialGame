def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x, y, a, b):
        return abs(a - x) + abs(b - y)

    def norm_dir(dx, dy):
        if dx > 1: dx = 1
        if dx < -1: dx = -1
        if dy > 1: dy = 1
        if dy < -1: dy = -1
        return dx, dy

    targets = []
    for key in ("unclaimed_cells", "unclaimed", "resources"):
        v = observation.get(key)
        if v:
            for t in v:
                if isinstance(t, (list, tuple)) and len(t) >= 2:
                    x, y = int(t[0]), int(t[1])
                    if inb(x, y) and (x, y) not in obstacles:
                        targets.append((x, y))
                elif isinstance(t, dict) and "x" in t and "y" in t:
                    x, y = int(t["x"]), int(t["y"])
                    if inb(x, y) and (x, y) not in obstacles:
                        targets.append((x, y))

    if not targets:
        targets = [(ox, oy)]
    targets = sorted(set(targets))

    tx, ty = sx, sy
    best = None
    for cx, cy in targets[:200]:
        d = dist(sx, sy, cx, cy)
        score = (d, cx, cy)
        if best is None or score < best:
            best = score
            tx, ty = cx, cy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_target = dist(nx, ny, tx, ty)
        d_to_opp = dist(nx, ny, ox, oy)
        val = (d_to_target, -d_to_opp, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]