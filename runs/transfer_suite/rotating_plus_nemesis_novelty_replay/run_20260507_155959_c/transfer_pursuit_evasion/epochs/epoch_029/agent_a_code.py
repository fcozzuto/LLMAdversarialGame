def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    role = str(observation.get("self_role", "")).lower()
    i_pursuer = "pursuer" in role or "pursuit" in role and "evader" not in role
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    INF = 10**9
    dist = [[INF] * w for _ in range(h)]
    if inb(ox, oy):
        dist[oy][ox] = 0
        qx, qy = [ox], [oy]
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

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    best_move = [0, 0]
    best_val = -INF if not i_pursuer else INF

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist[ny][nx]
        if d == INF:
            continue
        val = -d if not i_pursuer else d
        # Tie-break deterministically toward the farthest corner if evader, nearest if pursuer
        tb = abs(nx - target[0]) + abs(ny - target[1])
        key = (val, -tb if not i_pursuer else tb)
        if not i_pursuer:
            if key[0] > -best_val:
                best_val = -key[0]
                best_move = [dx, dy]
        else:
            if key[0] < best_val:
                best_val = key[0]
                best_move = [dx, dy]

    # If BFS couldn't reach, fallback to corner-directed move
    if best_move == [0, 0] and not inb(sx, sy):
        return [0, 0]
    if best_move == [0, 0] and dist[sy][sx] == INF:
        tx, ty = target if not i_pursuer else (ox, oy)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if inb(sx + dx, sy + dy):
            return [dx, dy]
        if inb(sx + dx, sy):
            return [dx, 0]
        if inb(sx, sy + dy):
            return [0, dy]
        return [0, 0]
    return best_move