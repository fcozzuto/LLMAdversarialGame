def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Maximize lead over opponent; then prefer closer-for-us; then deterministic spatial tie-break
        key = (od - sd, -sd, -(rx * 100 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (dx, dy) != (0, 0) and (nx, ny) in obstacles:
        # Try the dominant axis step that isn't blocked
        opts = []
        if dx != 0:
            opts.append((dx, 0))
        if dy != 0:
            opts.append((0, dy))
        if dx != 0 and dy != 0:
            # also allow stepping diagonally with swapped axis effect already covered by main
            pass
        moved = False
        for ddx, ddy in opts:
            tx, ty = sx + ddx, sy + ddy
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                dx, dy = ddx, ddy
                moved = True
                break
        if not moved:
            return [0, 0]

    return [dx, dy]