def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    role = observation.get("self_role", "pursuer")
    maximize = (str(role).lower() == "evader")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = int(sx + dx), int(sy + dy)
        if not inb(nx, ny):
            continue
        d = dist2(nx, ny, int(ox), int(oy))
        v = d if maximize else -d
        if best_val is None or v > best_val:
            best_val = v
            best_move = [dx, dy]

    return best_move