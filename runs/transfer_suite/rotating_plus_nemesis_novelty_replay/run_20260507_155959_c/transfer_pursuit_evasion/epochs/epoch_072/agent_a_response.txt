def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = []
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.append((int(x), int(y)))
        except Exception:
            pass
    obs = set(obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or role == "evader"

    def next_pos(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            return sx, sy
        return nx, ny

    def mindist_to_obs(x, y):
        if not obs:
            return 99
        best = 99
        for ax, ay in obs:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        return best

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                c += 1
        return c

    best = None
    best_move = [0, 0]

    if not is_evader:
        # Pursuer: chase while staying mobile and not trapping self near obstacles.
        for dx, dy in moves:
            nx, ny = next_pos(dx, dy)
            capture = (nx == ox and ny == oy)
            dist = abs(nx - ox) + abs(ny - oy)
            clear = mindist_to_obs(nx, ny)
            mob = mobility(nx, ny)
            # Prefer capture, then smaller distance, then more clear space, then more mobility.
            key = (0 if capture else 1, dist, -clear, -mob)
            if best is None or key < best:
                best = key
                best_move = [dx, dy]
    else:
        # Evader: flee while avoiding borders/obstacles; prefer moves that maximize distance and keep mobility.
        for dx, dy in moves:
            nx, ny = next_pos(dx, dy)
            dist = abs(nx - ox) + abs(ny - oy)
            clear = mindist_to_obs(nx, ny)
            mob = mobility(nx, ny)
            # Prefer larger distance, then more clearance, then more mobility; slight preference to not stay if tied.
            stay_pen = 1 if (dx == 0 and dy == 0) else 0
            key = (-dist, stay_pen, -clear, -mob)
            if best is None or key < best:
                best = key
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]