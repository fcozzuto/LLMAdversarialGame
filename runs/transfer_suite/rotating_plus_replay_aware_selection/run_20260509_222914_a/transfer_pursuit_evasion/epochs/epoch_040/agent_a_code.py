def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("evasion" in role)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def min_dist_to_obstacles(x, y):
        if not obstacles:
            return 10**6
        dmin = 10**6
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < dmin:
                dmin = d
        return dmin

    best_val = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        dist = max(abs(nx - ox), abs(ny - oy))
        if is_evader:
            obj = dist
        else:
            obj = -dist

        dmin = min_dist_to_obstacles(nx, ny)
        # Strongly avoid getting too close to obstacles
        obj += (dmin >= 2) * (0.5 + 1.5 / (dmin + 1)) - (dmin == 1) * 5.0 - (dmin == 0) * 1000.0

        # When evading, also prefer moves that keep momentum away from the pursuer
        vx, vy = nx - sx, ny - sy
        away_x = (1 if sx > ox else -1 if sx < ox else 0)
        away_y = (1 if sy > oy else -1 if sy < oy else 0)
        if is_evader:
            obj += 0.25 * (vx * away_x + vy * away_y)
        else:
            toward_x = -away_x
            toward_y = -away_y
            obj += 0.25 * (vx * toward_x + vy * toward_y)

        if best_val is None or obj > best_val:
            best_val = obj
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]