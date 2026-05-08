def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    is_evader = str(observation.get("self_role", "")).lower() == "evader"

    dist = [[-1] * w for _ in range(h)]
    if free(ox, oy):
        q = [(ox, oy)]
        dist[oy][ox] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if free(nx, ny) and dist[ny][nx] == -1:
                    dist[ny][nx] = nd
                    q.append((nx, ny))

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = dist[ny][nx]
        if d < 0:
            d = abs(nx - ox) + abs(ny - oy)
        val = d if is_evader else -d
        if best is None or val > best_val:
            best, best_val = [dx, dy], val

    if best is not None:
        return best

    dx = 0 if ox == sx else (1 if ox > sx else -1)
    dy = 0 if oy == sy else (1 if oy > sy else -1)
    return [-dx, -dy] if is_evader else [dx, dy]