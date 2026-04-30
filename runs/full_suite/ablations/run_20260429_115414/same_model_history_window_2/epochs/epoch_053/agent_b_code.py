def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    moves = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    res = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                res.append((rx, ry))

    def first_step_to(tx, ty, limit):
        if not inb(sx, sy) or not inb(tx, ty):
            return None
        if (sx, sy) == (tx, ty):
            return (0, 0)
        dist = [[-1] * h for _ in range(w)]
        prev = [[None] * h for _ in range(w)]
        q = [(sx, sy)]
        dist[sx][sy] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            d = dist[x][y]
            if d >= limit:
                continue
            nd = d + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and dist[nx][ny] < 0:
                    dist[nx][ny] = nd
                    prev[nx][ny] = (x, y)
                    if (nx, ny) == (tx, ty):
                        cx, cy = tx, ty
                        px, py = prev[cx][cy]
                        while (px, py) != (sx, sy):
                            cx, cy = px, py
                            px, py = prev[cx][cy]
                        return (cx - sx, cy - sy)
                    q.append((nx, ny))
        return None

    limit = 12
    best = None  # (dist, target, first_step)
    for i, (rx, ry) in enumerate(res):
        step = first_step_to(rx, ry, limit)
        if step is not None:
            md = abs(rx - sx) + abs(ry - sy)
            cand = (md, i, (rx, ry), step)
            if best is None or cand < (best[0], best[1], best[2], best[3]):
                best = (md, i, (rx, ry), step)

    if best is not None:
        dx, dy = best[3]
        return [int(dx), int(dy)]

    # Fallback: move toward opponent deterministically, avoiding obstacles when possible
    best_step = (0, 0)
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = -(abs(nx - ox) + abs(ny - oy))
        if val > best_val or (val == best_val and (dx, dy) < best_step):
            best_val = val
            best_step = (dx, dy)
    return [int(best_step[0]), int(best_step[1])]