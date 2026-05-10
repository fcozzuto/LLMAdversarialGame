def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    role = observation.get("self_role", "pursuer")
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def in_bounds_not_obs(x, y):
        return ok(x, y)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = [0, 0]
    best_val = None

    # Tie-break deterministically by fixed order of deltas (already deterministic)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if nx == ox and ny == oy and role == "pursuer":
            return [dx, dy]

        d = dist(nx, ny, ox, oy)

        # local obstacle pressure: count blocked adjacent cells (lower is better for pursuer, higher is safer for evader)
        blocked = 0
        for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ax, ay = nx + adx, ny + ady
            if not in_bounds_not_obs(ax, ay):
                blocked += 1

        # wall/corner preference
        cornerish = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)  # smaller => closer to wall/corner
        centerish = -((nx - cx) ** 2 + (ny - cy) ** 2)  # larger => closer to center

        if role == "pursuer":
            val = (-d * 10.0) + (centerish * 0.2) - (blocked * 0.6)
            # also prefer moves that keep direction aligned toward opponent (reduce zigzag)
            prev_dx = 0
            prev_dy = 0
            val += (0.1 if dx == 0 and dy == 0 else 0.0) + (0.05 * (1 if (nx - sx) * (ox - sx) >= 0 else -1))
            # minor deterministic preference to reduce risk of getting stuck near walls:
            val += (-cornerish * 0.05)
        else:  # evader
            val = (d * 10.0) - (blocked * 0.8)
            # strongly prefer corners/walls to limit pursuer paths
            val += (-cornerish * 0.6)
            # slight preference for staying away from center if it increases cornerish; keep deterministic
            val += (-centerish * 0.05)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move