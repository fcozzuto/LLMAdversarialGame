def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    role = str(observation.get("self_role", "")).lower()
    i_pursuer = "pursuer" in role
    i_evader = (not i_pursuer)  # default to evader if unclear

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
                    qx.append(nx); qy.append(ny)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist[ny][nx]
        if d == INF:
            # fallback: evader prefers far from opponent, pursuer prefers close
            man = abs(nx - ox) + abs(ny - oy)
            val = -man if i_pursuer else man
        else:
            # evader wants maximize distance; pursuer wants minimize distance
            val = -d if i_pursuer else d
        # tie-break deterministically toward far corner (evader) or opponent (pursuer)
        tie = (abs(nx - far_corner[0]) + abs(ny - far_corner[1])) if i_evader else (abs(nx - ox) + abs(ny - oy))
        if best is None or val > best_val or (val == best_val and tie < best[2]):
            best = (dx, dy, tie); best_val = val

    if best is None:
        dx = 0 if far_corner[0] == sx else (1 if far_corner[0] > sx else -1)
        dy = 0 if far_corner[1] == sy else (1 if far_corner[1] > sy else -1)
        dx = dx if inb(sx + dx, sy) else 0
        dy = dy if inb(sx, sy + dy) else 0
        return [dx, dy]
    return [best[0], best[1]]