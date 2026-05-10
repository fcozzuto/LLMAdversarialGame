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
    is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Prefer capture (pursuer) / maximize distance (evader), while avoiding obstacles and keeping deterministic tie-breaks.
    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            nx, ny = sx, sy  # engine keeps in place on invalid move
        dist = d2(nx, ny, ox, oy)

        # Corner bias to counter corner-drifting archetype.
        if ox >= w // 2:
            corner_x = 0
        else:
            corner_x = w - 1
        if oy >= h // 2:
            corner_y = 0
        else:
            corner_y = h - 1
        corner_dist = d2(nx, ny, corner_x, corner_y)

        # Obstacle proximity penalty (Manhattan) for smoother navigation.
        obs_pen = 0
        if obstacles:
            minmd = 999999
            for ax, ay in obstacles:
                md = abs(nx - ax) + abs(ny - ay)
                if md < minmd:
                    minmd = md
                    if minmd == 0:
                        break
            obs_pen = minmd

        if is_evader:
            # maximize distance to opponent; also drift toward chosen corner (away from opponent)
            val = (dist, -corner_dist, obs_pen, -nx, -ny)
            better = best is None or val > best_val
        else:
            # minimize distance to opponent; also drift toward opponent's likely corner
            val = (-dist, corner_dist, obs_pen, nx, ny)
            better = best is None or val > best_val

        if better:
            best = (dx, dy)
            best_val = val

    return [int(best[0]), int(best[1])]