def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "escape", "evasion"))
    if not is_evader and not any(k in role for k in ("pursuer", "chaser", "catcher")):
        is_evader = False

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs.sort()

    INF = 10**9
    dist = [[INF] * h for _ in range(w)]
    if 0 <= ox < w and 0 <= oy < h and (ox, oy) not in obstacles:
        q = [(ox, oy)]
        dist[ox][oy] = 0
        head = 0
        while head < len(q):
            x, y = q[head]
            head += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and dist[nx][ny] > nd:
                    dist[nx][ny] = nd
                    q.append((nx, ny))

    best = None
    if is_evader:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        far_corner = max(corners, key=lambda c: max(abs(c[0] - ox), abs(c[1] - oy)))
        tx, ty = far_corner
        best_key = (-INF, -INF)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            d = dist[nx][ny]
            prog = -(max(abs(nx - tx), abs(ny - ty)))
            key = (d if d < INF else 10**6, prog)
            if key > best_key:
                best_key = key
                best = (dx, dy)
    else:
        best_key = (INF, INF)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            d = dist[nx][ny]
            cheb = max(abs(nx - ox), abs(ny - oy))
            key = (d, cheb)
            if key < best_key:
                best_key = key
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]