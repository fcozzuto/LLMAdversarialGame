def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    ox, oy = observation["opponent_position"]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        best_sc = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                sc = -kdist(nx, ny, cx, cy)
                if sc > best_sc:
                    best_sc = sc
                    best = [dx, dy]
        return best

    # Choose a resource we can likely secure; score favors being earlier than opponent.
    best_res = resources[0]
    best_res_sc = -10**18
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        sd = kdist(sx, sy, rx, ry)
        od = kdist(ox, oy, rx, ry)
        # Prefer resources closer than opponent, then closer overall; slight tie-break by coordinates.
        sc = (od - sd) * 10 - sd - (rx * 0.01 + ry * 0.001)
        if sc > best_res_sc:
            best_res_sc = sc
            best_res = [rx, ry]

    tx, ty = best_res

    # If adjacent to target, don't waste steps; otherwise step toward it while avoiding obstacles.
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            # Also prefer moving that reduces the opponent advantage for the chosen target.
            sc = -kdist(nx, ny, tx, ty) * 3 + (kdist(ox, oy, tx, ty) - kdist(nx, ny, tx, ty))
            candidates.append((sc, dx, dy))
    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [candidates[0][1], candidates[0][2]]