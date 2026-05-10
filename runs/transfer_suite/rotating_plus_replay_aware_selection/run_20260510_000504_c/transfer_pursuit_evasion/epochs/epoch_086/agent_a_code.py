def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    # If we look like an evader, maximize distance; otherwise chase.
    self_is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role) or ("flee" in self_role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    # Corner target to bias evasion; if chasing, use corner to restrict opponent movement.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    best = None
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue

            d_opp = dist2(nx, ny, ox, oy)
            # Obstacle "nearby" penalty to avoid wall-running traps.
            near_obs = 0
            for ex, ey in obstacles:
                man = abs(nx - ex) + abs(ny - ey)
                if man == 0:
                    near_obs += 10000
                elif man <= 2:
                    near_obs += (3 - man) * 40

            # If chasing, prefer moves that reduce distance to opponent and steer toward/through open space.
            # If evading, prefer moves that increase distance and drift toward the farthest corner.
            if self_is_evader:
                corner_bias = -dist2(nx, ny, far_corner[0], far_corner[1])
                val = (d_opp * 3) + corner_bias - near_obs
            else:
                corner_bias = -dist2(nx, ny, near_corner[0], near_corner[1])
                val = (-d_opp * 3) + corner_bias - near_obs

            # Deterministic tie-break: lexical order on (dx,dy) by scanning order.
            if best is None or val > best_val:
                best = [dx, dy]
                best_val = val

    # If all moves blocked, stay.
    return best if best is not None else [0, 0]