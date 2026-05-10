def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
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

    self_role = observation.get("self_role", "") or ""
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Deterministic ordering for tie-breaks
    moves.sort()

    def nearest_obst_dist(x, y):
        best = 10**9
        for ox2, oy2 in obstacles:
            d = abs(x - ox2) + abs(y - oy2)
            if d < best:
                best = d
        return best if best != 10**9 else 99

    is_evader = ("evader" in self_role.lower()) or ("runner" in self_role.lower())
    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        # Evader: maximize distance; Pursuer: minimize distance.
        # Add small obstacle-separation term to avoid getting pinned.
        sep = nearest_obst_dist(nx, ny)
        score = (d + 0.03 * sep) if is_evader else (-(d) + 0.01 * sep)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]