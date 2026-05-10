def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    self_role = str(observation.get("self_role", "")).lower()
    self_is_pursuer = ("purs" in self_role) or ("catch" in self_role) or ("tag" in self_role)

    def blocked(x, y):
        for bx, by in obstacles:
            if bx == x and by == y:
                return True
        return False

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    vx, vy = ox - sx, oy - sy
    steps = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = None

    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue

        ddx, ddy = ox - nx, oy - ny
        dist2 = ddx * ddx + ddy * ddy

        # Center bias (helps pursuer to not chase along a wall endlessly)
        center2 = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)

        # Wall proximity / "escape from corners" for evader
        edge_dist = min(nx, ny, (w - 1) - nx, (h - 1) - ny)

        # Obstacle-aware steering: penalize moves that step next to obstacles too much
        near_obs = 0
        for bx, by in obstacles:
            if abs(bx - nx) + abs(by - ny) <= 1:
                near_obs += 1

        # Try to keep moving in same general direction (deterministic smoothing)
        move_dir_align = (ddx * (nx - sx) + ddy * (ny - sy))

        if self_is_pursuer:
            # maximize progress while reducing distance; prefer center and avoid hugging obstacles
            val = (-dist2) - 0.15 * center2 - 0.35 * near_obs + 0.02 * move_dir_align
        else:
            # maximize distance; keep edge_dist not too small (avoid getting trapped), and avoid obstacles
            val = (dist2) + 0.12 * (10 - edge_dist) - 0.4 * near_obs + 0.02 * (-move_dir_align)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move