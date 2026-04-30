def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_key = None
    for rx, ry in resources:
        sd = cd(sx, sy, rx, ry)
        od = cd(ox, oy, rx, ry)
        # Prefer resources where we have lead; then shorter distance; then nearer to center.
        lead = od - sd
        center = (abs(rx - cx) + abs(ry - cy))
        key = (lead, -sd, -center)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_md = None
    # Tie-break deterministically by move order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = cd(nx, ny, tx, ty)
        # Also discourage stepping away in case of equal distance
        prog = cd(sx, sy, tx, ty) - dist
        key = (prog, -dist)
        if best_md is None or key > best_md:
            best_md = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]