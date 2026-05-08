def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
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
        return dx if dx >= dy else dy

    # Target selection: prioritize resources we can reach earlier; otherwise, minimize "we-behindness"
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # earlier wins; if tied, prefer farther for opponent (smaller do is worse), then closer for us
        key = (0 if ds < do else 1, ds - do, do - ds, ds, rx, ry)
        if best is None or key < best_key:
            best = (rx, ry)
            best_key = key

    tx, ty = best

    # Move toward target while avoiding obstacles; deterministic tie-break by dx,dy ordering
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                dist = cheb(nx, ny, tx, ty)
                moves.append((dist, abs(dx) + abs(dy) * 0 + 0, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: (t[0], t[2] * 0 + t[3] * 0, t[2], t[3]))
    return [int(moves[0][2]), int(moves[0][3])]