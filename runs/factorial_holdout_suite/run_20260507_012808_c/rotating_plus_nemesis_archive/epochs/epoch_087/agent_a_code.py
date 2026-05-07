def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = None
    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # prefer reaching a resource quickly; deterministic tie-break by move order
            dmin = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
            score = dmin * 100 + (abs(nx - ox) + abs(ny - oy))  # also slightly keep away
            if best is None or score < best[0]:
                best = (score, dx, dy)
    else:
        # no visible resources: head toward opponent if that seems safer
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = (abs(nx - ox) + abs(ny - oy))  # minimize distance to opponent
            if best is None or score < best[0]:
                best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]