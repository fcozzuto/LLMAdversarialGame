def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    cap_r = observation.get("capture_radius", 0)
    self_role = str(observation.get("self_role", "pursuer")).lower()
    is_evader = "evader" in self_role

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def local_obs(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)]
    dirs = sorted(dirs, key=lambda d: (d[0], d[1]))

    best_move = [0, 0]
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Capture is immediate termination; prioritize capture when pursuing.
        if not is_evader and cap_r == 0 and nx == ox and ny == oy:
            return [dx, dy]

        cheb = max(abs(nx - ox), abs(ny - oy))
        man = abs(nx - ox) + abs(ny - oy)
        lo = local_obs(nx, ny)

        # Bias toward boundary-adjacent moves to handle wall-running opponents.
        boundary_dist = min(nx, ny, (w - 1) - nx, (h - 1) - ny)  # smaller => closer to edge
        edge_bias = -boundary_dist

        # When evading, avoid getting close; when pursuing, close distance.
        # Also discourage stepping into tight obstacle clusters.
        if is_evader:
            val = cheb * 4 + man + (-lo) * 2 + (-edge_bias) * 0.5
        else:
            val = -cheb * 4 - man - lo * 1.5 + edge_bias * 0.5

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move