def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("hunter" in self_role) or ("chaser" in self_role) or ("pursuit" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs_pref = [0, 2, 6, 8, 1, 3, 5, 7, 4]  # deterministic tie-break

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d_inf(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def min_manhattan_to_obstacles(x, y):
        if not obstacles:
            return 999
        best = 999
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    best_val = None
    best_move = (0, 0)

    for idx in dirs_pref:
        dx, dy = moves[idx]
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        dist = d_inf(nx, ny, ox, oy)
        obs_d = min_manhattan_to_obstacles(nx, ny)

        # Greedy: pursuer maximize progress (smaller distance), evader maximize separation (larger distance)
        # Add obstacle proximity penalty to avoid getting stuck.
        if is_pursuer:
            val = (-dist) + (0.25 * obs_d)  # prefer farther from obstacles while closing in
        else:
            val = (dist) + (0.25 * obs_d)  # prefer farther from pursuer while keeping safe from obstacles

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]