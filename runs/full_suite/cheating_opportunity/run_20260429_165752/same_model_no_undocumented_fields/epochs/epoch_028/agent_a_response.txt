def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    s = observation.get("self_position", [0, 0])
    o = observation.get("opponent_position", [0, 0])
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dxdy = [0, 0]
    best_val = -10**18

    center = (w // 2, h // 2)

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            val = -10**18
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Prefer moves that create distance advantage to a resource.
                cand = (do - ds) * 100 - ds
                if cand > val:
                    val = cand
            if val > best_val:
                best_val = val
                best_dxdy = [dx, dy]
    else:
        tx, ty = center
        # No visible resources: move toward center, but bias away from opponent if possible.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_center = cheb(nx, ny, tx, ty)
            d_opp = cheb(nx, ny, ox, oy)
            d_opp_cur = cheb(sx, sy, ox, oy)
            # If tie, prefer increasing opponent distance.
            val = -d_center * 10 + (d_opp - d_opp_cur)
            if val > best_val:
                best_val = val
                best_dxdy = [dx, dy]

    return [int(best_dxdy[0]), int(best_dxdy[1])]