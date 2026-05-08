def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = int(observation.get("self_position", [0, 0])[0]), int(observation.get("self_position", [0, 0])[1])
    px, py = int(observation.get("opponent_position", [0, 0])[0]), int(observation.get("opponent_position", [0, 0])[1])
    self_role = (observation.get("self_role", "") or "").lower()
    obstacles = observation.get("obstacles", []) or []
    ox = {(int(o[0]), int(o[1])) for o in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in ox:
                c += 1
        return c

    is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role)
    if self_role == "":
        is_evader = False  # fallback: assume pursuer

    best_dx, best_dy = 0, 0
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        nx = clamp(nx, 0, w - 1)
        ny = clamp(ny, 0, h - 1)
        if (nx, ny) in ox:
            continue

        dist = cheb(nx, ny, px, py)
        mobility = free_neighbors(nx, ny)

        if not is_evader:
            # pursuer: minimize distance, prefer mobility, deterministic tie-break by move order
            val = -dist + 0.03 * mobility
        else:
            # evader: maximize distance, prefer mobility, slightly avoid corners (distance from center)
            center_bonus = cheb(nx, ny, (w - 1) / 2.0, (h - 1) / 2.0)
            val = dist + 0.03 * mobility + 0.01 * center_bonus

        if best_val is None or val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]