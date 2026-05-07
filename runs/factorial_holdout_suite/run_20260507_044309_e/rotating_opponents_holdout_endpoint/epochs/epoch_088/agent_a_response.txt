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
        v = a - c
        if v < 0:
            v = -v
        u = b - d
        if u < 0:
            u = -u
        return v + u

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = (-10**18, 10**18, 10**18)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Evaluate next position by best attainable resource advantage vs opponent.
        # Primary: (opp_dist - our_dist) for that resource (bigger means we are more competitive).
        # Secondary: smaller our_dist to win tempo.
        # Tertiary: smaller opp_dist to that resource (deny chance).
        local_best = (-10**18, 10**18, 10**18)
        for tx, ty in resources:
            sd = man(nx, ny, tx, ty)
            if sd == 0:
                sd = 0
            od = man(ox, oy, tx, ty)
            key = (od - sd, sd, od)
            if key[0] > local_best[0] or (key[0] == local_best[0] and (key[1] < local_best[1] or (key[1] == local_best[1] and key[2] < local_best[2]))):
                local_best = key

        if local_best[0] > best_key[0] or (local_best[0] == best_key[0] and (local_best[1] < best_key[1] or (local_best[1] == best_key[1] and local_best[2] < best_key[2]))):
            best_key = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]