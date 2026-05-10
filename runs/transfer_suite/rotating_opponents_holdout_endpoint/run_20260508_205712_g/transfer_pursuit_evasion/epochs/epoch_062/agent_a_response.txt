def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "pursuer").lower()
    pursuer = (role != "evader")

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x, y):
        dx = x - ox
        dy = y - oy
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def blocked_neighbors(x, y):
        cnt = 0
        for ddx, ddy in deltas:
            nx, ny = x + ddx, y + ddy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                cnt += 1
        return cnt

    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = cheb(nx, ny)
        if pursuer and dist == 0:
            return [dx, dy]
        wall = blocked_neighbors(nx, ny)
        # Greedy chase/evade with wall-avoid to resist wall-running traps.
        if pursuer:
            key = (dist, wall, dx, dy)
        else:
            key = (-dist, wall, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]