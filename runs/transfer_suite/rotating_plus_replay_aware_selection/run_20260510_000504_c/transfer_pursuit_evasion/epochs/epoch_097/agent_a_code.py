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

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("escape" in role) or ("runner" in role) or ("flee" in role)

    INF = 10**9
    dist = [[INF] * h for _ in range(w)]
    if (ox, oy) not in obstacles:
        dist[ox][oy] = 0
        q = [(ox, oy)]
        head = 0
        steps = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        while head < len(q):
            x, y = q[head]
            head += 1
            nd = dist[x][y] + 1
            for dx, dy in steps:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    if nd < dist[nx][ny]:
                        dist[nx][ny] = nd
                        q.append((nx, ny))

    best = None
    best_val = None
    candidates = []
    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        candidates.append((dx, dy, nx, ny))

    center_pref = (sx - (w - 1) / 2.0, sy - (h - 1) / 2.0)
    pref_center = abs(center_pref[0]) + abs(center_pref[1])

    for dx, dy, nx, ny in candidates:
        d = dist[nx][ny]
        if d >= INF:
            d = 10**6
        if is_evader:
            val = (-d, abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0), dx, dy)
        else:
            val = (d, abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0), -dx, -dy)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]