def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    sr = str(observation.get("self_role", "")).lower()
    i_am_evader = ("evader" in sr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    INF = 10**9
    dist = [[INF] * w for _ in range(h)]
    if inb(ox, oy):
        qx, qy = [ox], [oy]
        dist[oy][ox] = 0
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[y][x] + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx)
                    qy.append(ny)

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Score candidate move: for pursuer minimize distance to opponent; for evader maximize.
    best_move = [0, 0]
    best_val = -INF if i_am_evader else INF

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist[ny][nx]
        if d >= INF:
            # If unreachable due to obstacles, prefer depending on role.
            val = (10**6) if i_am_evader else (-10**6)
        else:
            # Add slight tie-breaker toward/opposite Manhattan distance to avoid dithering.
            md = manh(nx, ny, ox, oy)
            if i_am_evader:
                val = d * 1000 + md
            else:
                val = -d * 1000 - md

        if i_am_evader:
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
            elif val == best_val:
                if abs(dx) + abs(dy) < abs(best_move[0]) + abs(best_move[1]):
                    best_move = [dx, dy]
        else:
            if val < best_val:
                best_val = val
                best_move = [dx, dy]
            elif val == best_val:
                if abs(dx) + abs(dy) > abs(best_move[0]) + abs(best_move[1]):
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]