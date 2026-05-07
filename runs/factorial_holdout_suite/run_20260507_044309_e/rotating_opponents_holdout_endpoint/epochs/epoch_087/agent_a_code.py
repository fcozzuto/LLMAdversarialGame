def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    def cell_score(px, py):
        best = (-10**18, 10**9)
        for tx, ty in resources:
            sd = man(px, py, tx, ty)
            od = man(ox, oy, tx, ty)
            # Prefer moves that keep us closer to some resource than opponent.
            # Tie-break by closer resource for faster collection.
            key = (od - sd, sd)
            if key[0] > best[0] or (key[0] == best[0] and key[1] < best[1]):
                best = key
        return best[0], best[1]

    best_move = (0, 0)
    best_key = (-10**18, 10**9)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                k0, k1 = cell_score(nx, ny)
                # Secondary tie: move that reduces distance to opponent (prevents us being blocked by races)
                k2 = man(nx, ny, ox, oy)
                key = (k0, -k1, -k2)
                if key[0] > best_key[0] or (key[0] == best_key[0] and (-k1, -k2) > (-(best_key[1]), 0)):
                    best_key = (k0, k1)
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]