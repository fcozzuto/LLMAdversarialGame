def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    role = str(observation.get("self_role", "")).lower()
    is_evader = (role == "evader")

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

    # BFS distances from opponent (useful for pursuer chase and evader flee)
    dist = [[-1] * w for _ in range(h)]
    if free(ox, oy):
        qx, qy = [ox], [oy]
        dist[oy][ox] = 0
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if free(nx, ny) and dist[ny][nx] == -1:
                    dist[ny][nx] = nd
                    qx.append(nx)
                    qy.append(ny)

    if is_evader:
        # Maximize distance to pursuer; bias toward farthest-from-opponent corner deterministically.
        tx = 0 if ox >= (w - 1) / 2 else (w - 1)
        ty = 0 if oy >= (h - 1) / 2 else (h - 1)
        best = None
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = dist[ny][nx]
            if d < 0:
                d = 10**9  # unreachable: treat as very safe
            corner_bias = (abs(tx - nx) + abs(ty - ny))
            val = (d, corner_bias, -nx, -ny, dx, dy)
            if best is None or val > best_val:
                best = [dx, dy]
                best_val = val
        return best if best is not None else [0, 0]

    # Pursuer: minimize distance to evader; if unreachable, greedy toward opponent.
    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = dist[ny][nx]
        if d < 0:
            # unreachable: use Manhattan/chebyshev-ish greedy as fallback
            d = max(abs(ox - nx), abs(oy - ny)) + 10**6
        val = (-d, -(abs(ox - nx) + abs(oy - ny)), nx, ny, dx, dy)
        if best is None or val > best_val:
            best = [dx, dy]
            best_val = val
    return best if best is not None else [0, 0]