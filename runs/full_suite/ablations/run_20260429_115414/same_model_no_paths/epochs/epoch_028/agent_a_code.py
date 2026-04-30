def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cand = [(sx + dx, sy + dy) for dx, dy in dirs if valid(sx + dx, sy + dy)]
    if not cand:
        return [0, 0]

    if resources:
        best = None
        best_sc = -10**18
        for nx, ny in cand:
            d_self = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            d_opp = cheb(nx, ny, ox, oy)
            sc = -d_self * 1000 + d_opp
            if best is None or sc > best_sc or (sc == best_sc and (nx, ny) < best):
                best_sc = sc
                best = (nx, ny)
        return [best[0] - sx, best[1] - sy]

    best = None
    best_sc = -10**18
    for nx, ny in cand:
        sc = cheb(nx, ny, ox, oy)
        if best is None or sc > best_sc or (sc == best_sc and (nx, ny) < best):
            best_sc = sc
            best = (nx, ny)
    return [best[0] - sx, best[1] - sy]