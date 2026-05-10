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
    steps = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if (ox, oy) not in obstacles:
        dist[ox][oy] = 0
        q = [(ox, oy)]
        head = 0
        while head < len(q):
            x, y = q[head]
            head += 1
            nd = dist[x][y] + 1
            for dx, dy in steps:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))

    best_cell = (sx, sy)
    best_score = -INF if is_evader else INF
    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d = dist[nx][ny]
        if d >= INF:
            continue
        manh = abs(nx - ox) + abs(ny - oy)
        score = (d * 10 + manh) if is_evader else (-(d * 10 + manh))
        if (is_evader and score > best_score) or ((not is_evader) and score < best_score):
            best_score = score
            best_cell = (nx, ny)

    dx = best_cell[0] - sx
    dy = best_cell[1] - sy
    if dx < -1 or dx > 1: dx = 0
    if dy < -1 or dy > 1: dy = 0
    return [int(dx), int(dy)]