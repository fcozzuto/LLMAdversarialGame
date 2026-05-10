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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    self_role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in self_role) or ("runner" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves.sort()

    def nearest_obst_penalty(x, y):
        if not obstacles:
            return 0
        best = 10**9
        for a, b in obstacles:
            d = abs(x - a) + abs(y - b)
            if d < best:
                best = d
        if best <= 1:
            return 50
        if best == 2:
            return 15
        if best == 3:
            return 7
        if best == 4:
            return 3
        return 0

    best_dx, best_dy = 0, 0
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        pen = nearest_obst_penalty(nx, ny)
        # Evader: maximize distance; Pursuer: minimize distance.
        val = dist - pen if is_evader else -dist - pen
        if best_val is None or val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]