def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if start in obstacles or not (0 <= start[0] < w and 0 <= start[1] < h):
            return dist
        qx, qy = [start[0]], [start[1]]
        dist[start[0]][start[1]] = 0
        head = 0
        while head < len(qx):
            x, y = qx[head], qy[head]
            head += 1
            d = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    if d < dist[nx][ny]:
                        dist[nx][ny] = d
                        qx.append(nx)
                        qy.append(ny)
        return dist

    d_me = bfs((sx, sy))
    d_op = bfs((ox, oy))

    best = None
    best_score = -10**18
    for r in resources:
        rm, ro = d_me[r[0]][r[1]], d_op[r[0]][r[1]]
        if rm >= 10**8 and ro >= 10**8:
            continue
        if ro < 10**8 and rm < 10**8:
            adv = (ro - rm) * 10 - rm
        else:
            adv = -rm if ro >= 10**8 else ro - rm * 2
        if adv > best_score:
            best_score = adv
            best = r

    tx, ty = best
    curd = d_me[sx][sy]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            candidates.append((d_me[nx][ny], dx, dy))
    candidates.sort(key=lambda t: (t[0], abs(t[1]) + abs(t[2]), t[1], t[2]))
    chosen = candidates[0] if candidates else (curd, 0, 0)
    return [int(chosen[1]), int(chosen[2])]