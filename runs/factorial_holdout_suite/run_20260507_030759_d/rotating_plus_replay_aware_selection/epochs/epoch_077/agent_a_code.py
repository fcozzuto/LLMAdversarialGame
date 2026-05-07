def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    if w <= 0 or h <= 0:
        return [0, 0]
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(x1, y1, x2, y2):
        return max(abs(x2 - x1), abs(y2 - y1))

    resources = observation.get("resources") or []
    targets = []
    for r in resources:
        if isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                x, y = r["position"][0], r["position"][1]
            else:
                x, y = r.get("x"), r.get("y")
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
        else:
            continue
        try:
            x, y = int(x), int(y)
        except:
            continue
        if inb(x, y):
            targets.append((x, y))

    if not targets:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dself = min(dist(nx, ny, tx, ty) for tx, ty in targets)
        dop = min(dist(ox, oy, tx, ty) for tx, ty in targets)
        score = dself * 1000 - dop  # smaller is better for self; tie keeps pressure on opponent
        diag_pref = 0 if (dx != 0 and dy != 0) else 1
        key = (score, diag_pref, -dx, -dy)
        if best_score is None or key < best_score:
            best_score = key
            best_move = [dx, dy]
    return best_move