def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            try:
                obs.add((int(p[0]), int(p[1])))
            except:
                pass

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = observation.get("resources") or []
    if resources:
        best_r = None
        best_key = None
        for r in resources:
            if not r or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if not in_bounds(rx, ry):
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer being closer than opponent; tie-break by absolute closeness
            key = (-(do - ds), ds, (rx + 17 * ry) % 13)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        if best_r is None:
            best_r = (ox, oy)
        tx, ty = best_r
    else:
        tx, ty = ox, oy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Main goal: reduce distance to target; secondary: keep away from opponent; small preference for staying/more direct moves
        val = (d_self, -d_opp, dx * dx + dy * dy, (nx + 31 * ny) % 7)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]