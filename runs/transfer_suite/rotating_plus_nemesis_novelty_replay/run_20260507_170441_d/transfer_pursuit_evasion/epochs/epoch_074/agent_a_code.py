def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    self_role = (observation.get("self_role", "") or "").lower()
    evader = ("evader" in self_role) or ("runner" in self_role) or ("escape" in self_role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dxdy = [0, 0]
    best_val = None

    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target = max(corners, key=lambda c: md(sx, sy, c[0], c[1])) if evader else (ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        d_opp = md(nx, ny, ox, oy)

        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj_obs += 1

        if evader:
            d_t = md(nx, ny, target[0], target[1])
            val = (d_opp * 2.2) + (d_t * 1.0) - (adj_obs * 3.0) - (0.01 * (nx + ny))
            better = best_val is None or val > best_val
        else:
            # pursuer: strongly minimize distance to opponent, also prefer reducing both axes
            d_next = d_opp
            axis = (abs(nx - ox) + abs(ny - oy))
            val = (-d_next * 2.5) + (-axis * 0.7) - (adj_obs * 1.7) + (0.01 * (nx - ny))
            better = best_val is None or val > best_val

        if better:
            best_val = val
            best_dxdy = [dx, dy]

    return best_dxdy