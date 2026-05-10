def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    cr = observation.get("capture_radius", 0)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        a = abs(x1 - x2)
        b = abs(y1 - y2)
        return a if a > b else b

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = sorted(dirs, key=lambda d: (d[0], d[1]))

    role = str(observation.get("self_role", "pursuer")).lower()
    is_evader = role == "evader"

    best_dx, best_dy = 0, 0
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        cap = 1 if (cr == 0 and nx == ox and ny == oy) else 0
        d = cheb(nx, ny, ox, oy)
        man = abs(nx - ox) + abs(ny - oy)

        # local obstacle risk: penalize being adjacent to obstacles (but allow if it helps capture)
        adj = 0
        for tx, ty in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)):
            ax, ay = nx + tx, ny + ty
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obstacles:
                adj += 1

        # wall proximity penalty
        wall = 0
        if nx == 0 or nx == w - 1:
            wall += 1
        if ny == 0 or ny == h - 1:
            wall += 1

        # Score: pursuer minimize distance; evader maximize distance.
        # Add capture dominance and keep behavior robust around obstacles.
        if cap:
            val = 10_000 if not is_evader else -10_000
        else:
            if is_evader:
                val = (d * 12) + (man * 3) - (adj * 2) - (wall * 2)
            else:
                val = (-d * 12) + (-man * 3) - (adj * 2) - (wall * 2)

        if best_val is None or (val > best_val):
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]