def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            unclaimed.append((int(p[0]), int(p[1])))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            resources.append((int(p[0]), int(p[1])))

    targets = resources if resources else unclaimed
    if targets:
        tx, ty = min(targets, key=lambda q: abs(q[0] - sx) + abs(q[1] - sy))
    else:
        tx, ty = (ox, oy) if (w * h > 1) else (sx, sy)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        score = abs(nx - tx) + abs(ny - ty)
        if best is None or score < best[0]:
            best = (score, dx, dy)
    if best is not None:
        return [best[1], best[2]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
    return [0, 0]