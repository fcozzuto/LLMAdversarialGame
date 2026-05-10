def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    unclaimed = observation.get("unclaimed_cells", []) or []
    targets = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obs:
                targets.append((x, y))
    if targets:
        targets.sort(key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
        targets = targets[:20]
    else:
        op = observation.get("opponent_position", None) or [sx, sy]
        tx, ty = op[0], op[1]
        targets = [(tx, ty)]

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        md = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
        score = (md, abs(dx) + abs(dy))
        if best_score is None or score < best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best