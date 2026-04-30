def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18
    have_res = bool(resources)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if have_res:
            dmin = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < dmin:
                    dmin = d
            # maximize score: go closer to nearest resource, avoid opponent, prefer staying
            score = -dmin * 10 - cheb(nx, ny, ox, oy) + (1 if dx == 0 and dy == 0 else 0)
        else:
            # no known resources: go away from opponent and toward center
            cx, cy = (w - 1) // 2, (h - 1) // 2
            score = cheb(nx, ny, ox, oy) * 2 - (cheb(nx, ny, cx, cy))
        if score > best_score:
            best_score = score
            best = [dx, dy]
    return best if best is not None else [0, 0]