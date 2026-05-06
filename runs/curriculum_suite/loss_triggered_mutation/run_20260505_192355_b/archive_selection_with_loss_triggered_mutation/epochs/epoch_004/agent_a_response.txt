def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", []) or []
    obst = set((int(p[0]), int(p[1])) for p in obstacles if p is not None and len(p) >= 2)
    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (sx, sy)
    best_val = -10**18

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue
        if not res:
            # fallback: drift to opponent side along safe-ish axis
            target_x = 0 if sx > w - 1 else w - 1
            target_y = h - 1 if sy < h - 1 else 0
            val = -cheb(nx, ny, target_x, target_y)
        else:
            # pick target resource that we can beat the opponent to; also reward denying by moving away from opponent's closest options
            val = 0
            for rx, ry in res:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # main: maximize advantage over opponent; secondary: prefer closer overall
                val2 = (opd - myd) * 100 - myd
                # slight tie-break: avoid moving towards opponent when resources are contested
                if opd <= myd + 1:
                    val2 -= cheb(nx, ny, ox, oy) * 2
                if val2 > val:
                    val = val2
        if val > best_val:
            best_val = val
            best = (nx, ny)

    return [best[0] - sx, best[1] - sy]