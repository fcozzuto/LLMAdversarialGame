def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    self_role = observation.get("self_role", "") or ""
    opponent_role = observation.get("opponent_role", "") or ""
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            obs.add((int(b[0]), int(b[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obs
    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx*dx + dy*dy

    # Heuristic role inference
    is_pursuer = ("pursuer" in self_role.lower()) or ("pursue" in self_role.lower())
    if not is_pursuer:
        if "pursuer" in opponent_role.lower():
            is_pursuer = False

    # Deterministic move ordering
    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)

        # Obstacle-aware bias: prefer moves that have more free neighbors (stability)
        free = 0
        for adx, ady in deltas:
            tx, ty = nx + adx, ny + ady
            if valid(tx, ty):
                free += 1

        # Pursuer: minimize distance; Evader: maximize distance and free-space
        if is_pursuer:
            score = -d + 0.01 * free
        else:
            score = d + 0.005 * free

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]