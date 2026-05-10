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
    if (ox, oy) not in obstacles:
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

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d = dist[nx][ny]
        # Tie-break deterministically by preferring steps that also change x, then y.
        tie = (abs(dx) + abs(dy), dx, dy)
        if d >= INF:
            d = 999999
        # If evader: maximize distance; else: minimize distance.
        key = (d if is_evader else -d, -tie[0], -tie[1], -tie[2], dx, dy)
        if best is None or key > best_key:
            best = [dx, dy]
            best_key = key
    return best if best is not None else [0, 0]