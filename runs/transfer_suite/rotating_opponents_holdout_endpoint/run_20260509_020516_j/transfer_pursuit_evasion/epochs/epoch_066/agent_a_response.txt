def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = map(int, observation.get("self_position") or [0, 0])
    ox, oy = map(int, observation.get("opponent_position") or [0, 0])
    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    evader = ("evader" in self_role) or ("pursuer" in self_role and "evader" in opp_role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # deterministic preference order: avoid staying if tied, then up-left, up, up-right, left, right, down-left, down, down-right
    order = {(0, 0): 100, (-1, -1): 0, (0, -1): 1, (1, -1): 2, (-1, 0): 3, (1, 0): 4, (-1, 1): 5, (0, 1): 6, (1, 1): 7}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    best = None
    best_key = None

    if evader:
        # Wall-run: keep near a boundary and avoid moves that allow immediate contact (distance 0).
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d2 = dist2(nx, ny)
            if d2 == 0:
                continue
            # closeness to any wall (maximize), and discourage going straight toward opponent
            wall = max(nx, w - 1 - nx, ny, h - 1 - ny)
            # Prefer moves that increase distance, then keep wall close (small wall distance), so maximize inverse
            key = (d2, -wall, -((nx - ox) * (sx - ox) + (ny - oy) * (sy - oy)), -order[(dx, dy)])
            if best_key is None or key > best_key:
                best_key, best = key, [dx, dy]
    else:
        # Pursuer: greedy reduce distance; if blocked, bias toward moves that likely re-open paths around obstacles.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d2 = dist2(nx, ny)
            # secondary: favor positions that have more free neighboring cells
            free = 0
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if inb(tx, ty):
                    free += 1
            key = (-d2, -free, -order[(dx, dy)])
            if best_key is None or key > best_key:
                best_key, best = key, [dx, dy]

        if best is None:
            return [0, 0]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]