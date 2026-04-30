def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def d(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Score a target resource: how much closer we are than opponent, prefer safer tiles.
    best_r = None
    best_sc = -10**18
    for rx, ry in resources:
        if (rx, ry) in occ:
            continue
        ds = d(sx, sy, rx, ry)
        doo = d(ox, oy, rx, ry)
        near_opp = d(rx, ry, ox, oy)
        safety = 0
        # Penalize adjacency to obstacles and being too close to opponent.
        for ax, ay in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nx, ny = rx + ax, ry + ay
            if (nx, ny) in occ:
                safety += 2 if (ax == 0 or ay == 0) else 1
        opp_pen = 0
        if near_opp <= 1:
            opp_pen = 80
        elif near_opp == 2:
            opp_pen = 30
        sc = (doo - ds) * 40 - ds - safety * 6 - opp_pen
        if sc > best_sc or (sc == best_sc and (best_r is None or (rx, ry) < best_r)):
            best_sc = sc
            best_r = (rx, ry)

    rx, ry = best_r
    # Greedy one-step move toward chosen target with obstacle avoidance.
    tx, ty = rx - sx, ry - sy
    preferred = []
    # Deterministic ordering: closer to target first by projection onto delta.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        # Compute next score directly for tie-breaking.
        proj = dx * (1 if tx > 0 else (-1 if tx < 0 else 0)) + dy * (1 if ty > 0 else (-1 if ty < 0 else 0))
        cur_sc = 0
        cur_sc += (d(nx, ny, ox, oy) - d(nx, ny, rx, ry)) * 10
        cur_sc -= d(nx, ny, rx, ry) * 2
        if d(nx, ny, ox, oy) <= 1:
            cur_sc -= 50
        # Obstacle proximity penalty.
        adj = 0
        for ax, ay in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            if (nx + ax, ny + ay) in occ:
                adj += 1
        cur_sc -= adj * 5
        preferred.append((cur_sc, proj, (dx, dy), nx, ny))

    if not preferred:
        return [0, 0]

    preferred.sort(key=lambda t: (t[0], t[1], -t[3], -t[4]), reverse=True)
    return [preferred[0][2][0], preferred[0][2][1]]