def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    roles = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    is_pursuer = ("pursuer" in roles) or ("evader" not in roles)
    obs = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2: obs.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def bfs_dist(startx, starty):
        INF = 10**9
        dist = [[INF]*w for _ in range(h)]
        qx, qy = [startx], [starty]
        dist[starty][startx] = 0
        head = 0
        while head < len(qx):
            x, y = qx[head], qy[head]; head += 1
            d = dist[y][x] + 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0: 
                        continue
                    nx, ny = x + dx, y + dy
                    if inb(nx, ny) and d < dist[ny][nx]:
                        dist[ny][nx] = d
                        qx.append(nx); qy.append(ny)
        return dist

    opp_dist = bfs_dist(ox, oy)  # distance from every cell to opponent
    INF = 10**9
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best = None
    best_val = None
    # Pursuer: minimize distance to opponent; Evader: maximize it.
    for dx, dy, nx, ny in moves:
        d = opp_dist[ny][nx]
        val = d if not is_pursuer else -d
        # Prefer closer/farther in reachability; then prefer moves that reduce chance of being blocked by obstacles:
        # deterministic tie-break by scanning order and then by Chebyshev change toward/away.
        if d >= INF: val += (-1000000 if is_pursuer else 1000000)
        if best is None or val > best_val:
            best_val = val; best = (dx, dy)

    return [int(best[0]), int(best[1])]