def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    is_pursuer = any(k in sr for k in ("pursuer", "hunter", "chaser"))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs_from(src):
        qx, qy = [src[0]], [src[1]]
        dist = {(src[0], src[1]): 0}
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[(x, y)] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in dist:
                    dist[(nx, ny)] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    dist = bfs_from((sx, sy))
    # If opponent unreachable, fall back to safest corner move
    if (ox, oy) not in dist:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
        for m in candidates:
            nx, ny = sx + m[0], sy + m[1]
            if inb(nx, ny):
                return [int(m[0]), int(m[1])]
        return [0, 0]

    def eval_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            return None
        d = dist.get((nx, ny), 10**9)
        # pursuer: minimize shortest-path distance; evader: maximize distance and prefer moving away from opponent directionally
        man = abs(nx - ox) + abs(ny - oy)
        edge = (nx == 0) or (nx == w - 1) or (ny == 0) or (ny == h - 1)
        if is_pursuer:
            return (-d, man, edge, -abs(dx) - abs(dy))
        else:
            return (d, man, edge, abs(dx) + abs(dy))

    best = None
    best_m = (0, 0)
    for dx, dy in moves:
        val = eval_move(dx, dy)
        if val is None:
            continue
        if best is None or val > best:
            best = val
            best_m = (dx, dy)
    nx, ny = sx + best_m[0], sy + best_m[1]
    if not inb(nx, ny):
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]