def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obstacle_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacle_set.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    resset = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obstacle_set and (x, y) != (sx, sy):
                resset.append((x, y))

    if not resset:
        return [0, 0]

    best = resset[0]
    best_key = None
    for rx, ry in resset:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        key = (od - sd, -sd, -abs(rx - sx), -abs(ry - sy), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = (0, 0)
    bestk = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacle_set:
            continue
        nsd = dist(nx, ny, tx, ty)
        nod = dist(ox, oy, tx, ty)
        step_key = (nod - nsd, -nsd, -abs(tx - nx) - abs(ty - ny), -dx, -dy)
        if bestk is None or step_key > bestk:
            bestk = step_key
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]