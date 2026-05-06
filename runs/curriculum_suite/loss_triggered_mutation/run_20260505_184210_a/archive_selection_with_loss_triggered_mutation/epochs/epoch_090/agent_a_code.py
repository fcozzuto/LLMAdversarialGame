def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])

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

    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    deltas = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    if resources:
        near = None
        bestd = None
        for x, y in resources:
            d = abs(x - sx) + abs(y - sy)
            if bestd is None or d < bestd or (d == bestd and (x, y) < near):
                bestd = d
                near = (x, y)
        tx, ty = near
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = abs(tx - nx) + abs(ty - ny)
            key = (d, abs(dx) + abs(dy), nx, ny)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        if best is not None:
            return [int(best[1]), int(best[2])]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [int(dx), int(dy)]
    return [0, 0]