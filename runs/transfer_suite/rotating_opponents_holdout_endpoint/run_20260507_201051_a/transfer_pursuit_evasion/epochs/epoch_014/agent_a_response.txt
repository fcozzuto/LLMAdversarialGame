def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    is_evader = str(observation.get("self_role", "")).lower() == "evader"

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

    def clearance(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if free(nx, ny):
                c += 1
        return c

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = dist[ny][nx] if 0 <= ny < h and 0 <= nx < w else -1
        if d == -1:
            # Unreachable from opponent: prefer moves with larger distance to keep away from capture routes
            d = 10_000 - (abs(nx - ox) + abs(ny - oy))
        # Tie-break: keep options open (avoid wall-running traps for evader / keep mobility for pursuer)
        c = clearance(nx, ny)
        # Secondary tie-break: bias toward staying near own corner direction relative to opponent
        bias = (nx + ny) - (ox + oy)
        key = ((-d) if is_evader else d, -c, -bias if is_evader else bias, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]