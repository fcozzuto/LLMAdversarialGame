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

    self_role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role) or ("flee" in self_role)

    INF = 10**9
    dist = [[INF] * h for _ in range(w)]
    if (ox, oy) in obstacles:
        dist[ox][oy] = 0
    else:
        dist[ox][oy] = 0
        q = [(ox, oy)]
        head = 0
        steps = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        while head < len(q):
            x, y = q[head]
            head += 1
            d0 = dist[x][y] + 1
            for dx, dy in steps:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    if d0 < dist[nx][ny]:
                        dist[nx][ny] = d0
                        q.append((nx, ny))

    best = None
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            d = dist[nx][ny]
            if d >= INF:
                val = -INF if is_evader else INF
            else:
                val = d if is_evader else -d
            # tie-break deterministically: prefer smaller dx, then smaller dy, then staying if possible
            key = (val, -abs(dx) - abs(dy), -int(dx == 0 and dy == 0), -dx, -dy) if is_evader else (val, -abs(dx) - abs(dy), -int(dx == 0 and dy == 0), -dx, -dy)
            if best is None or key > best_val:
                best = (dx, dy)
                best_val = key

    if best is None:
        return [0, 0]
    return [best[0], best[1]]