def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def bfs(start):
        if not inb(start[0], start[1]):
            return None
        dist = [[-1] * h for _ in range(w)]
        qx = [start[0]]
        qy = [start[1]]
        dist[start[0]][start[1]] = 0
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and dist[nx][ny] == -1:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    dself = bfs((sx, sy))
    dop = bfs((ox, oy))
    if dself is None or dop is None or not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        a = dself[rx][ry]
        b = dop[rx][ry]
        if a < 0 or b < 0:
            continue
        adv = b - a  # positive means we are closer
        key = (-adv, a, abs(rx - ox) + abs(ry - oy), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    if (sx, sy) == (tx, ty):
        return [0, 0]

    curd = dself[sx][sy]
    best_step = (0, 0)
    best_step_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = dself[nx][ny]
        if nd < 0:
            continue
        if nd > curd:  # discourage moving away
            continue
        step_key = (nd, dx, dy)
        if best_step_key is None or step_key < best_step_key:
            best_step_key = step_key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]