def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx = int(sp[0]) if isinstance(sp, (list, tuple)) and len(sp) > 0 else 0
    sy = int(sp[1]) if isinstance(sp, (list, tuple)) and len(sp) > 1 else 0
    ox = int(op[0]) if isinstance(op, (list, tuple)) and len(op) > 0 else 0
    oy = int(op[1]) if isinstance(op, (list, tuple)) and len(op) > 1 else 0

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cx = (w - 1) * 0.5
    cy = (h - 1) * 0.5

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        vd = 0
        for (rx, ry) in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            center = abs(rx - cx) + abs(ry - cy)
            vd += (od - sd) - 0.01 * center
        if vd > bestv:
            bestv = vd
            best = [dx, dy]

    return best if best is not None else [0, 0]