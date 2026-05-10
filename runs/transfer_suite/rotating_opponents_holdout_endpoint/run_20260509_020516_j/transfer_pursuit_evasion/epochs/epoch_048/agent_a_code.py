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
        is_evader = False  # default to pursuer

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs.sort()

    INF = 10**9
    dist = [[INF] * h for _ in range(w)]
    q = []
    if 0 <= ox < w and 0 <= oy < h and (ox, oy) not in obstacles:
        dist[ox][oy] = 0
        q.append((ox, oy))
    head = 0
    while head < len(q):
        x, y = q[head]
        head += 1
        nd = dist[x][y] + 1
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[nx][ny]:
                dist[nx][ny] = nd
                q.append((nx, ny))

    best_move = (0, 0)
    best_val = -INF if is_evader else INF
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d = dist[nx][ny]
        if d >= INF:
            d = 2 * (w + h)
        if is_evader:
            if d > best_val:
                best_val = d
                best_move = (dx, dy)
        else:
            if d < best_val:
                best_val = d
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]