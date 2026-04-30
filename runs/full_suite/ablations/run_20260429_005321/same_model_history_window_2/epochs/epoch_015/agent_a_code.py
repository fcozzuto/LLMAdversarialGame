def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obst.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
            res.append((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best = (10**9, 0, 0)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def score_move(nx, ny):
        if (nx, ny) in obst:
            return 10**8
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return 10**8
        if res:
            d_self = min(cheb(nx, ny, rx, ry) for rx, ry in res)
            d_opp = min(cheb(ox, oy, rx, ry) for rx, ry in res)
            # Prefer being closer to nearest resource than opponent.
            s = (d_self - d_opp) * 100
            # Small deterministic tie-break: prefer advancing towards center.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            s += cheb(nx, ny, int(cx), int(cy)) * 2
            return s
        # No resources provided: stay or move away from obstacles/edges minimally.
        edge_pen = 0
        if nx == 0 or nx == w - 1:
            edge_pen += 3
        if ny == 0 or ny == h - 1:
            edge_pen += 3
        return edge_pen + cheb(nx, ny, ox, oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        s = score_move(nx, ny)
        if s < best[0]:
            best = (s, dx, dy)

    return [int(best[1]), int(best[2])]