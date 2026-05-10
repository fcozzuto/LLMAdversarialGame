def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for x, y in resources:
        ds = cheb(x, y, sx, sy)
        do = cheb(x, y, ox, oy)
        # Relative advantage: prefer resources we can reach earlier by distance gap.
        adv = do - ds
        # If tied, prefer closer to us; if still tied, prefer deterministic smallest coords.
        key = (adv, -ds, -do, x, y)
        if best is None or key > best_key:
            best, best_key = (x, y), key

    tx, ty = best

    # Greedy step toward target with obstacle-safe tie-breaking.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestd = None
    bestk = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = cheb(nx, ny, tx, ty)
        # If we cannot get an advantage (adv<=0), still move as efficiently as possible.
        move_key = (-(dist), abs(dx) + abs(dy), nx, ny)
        if bestd is None or move_key > bestk:
            bestd, bestk = [dx, dy], move_key

    if bestd is None:
        return [0, 0]
    return bestd