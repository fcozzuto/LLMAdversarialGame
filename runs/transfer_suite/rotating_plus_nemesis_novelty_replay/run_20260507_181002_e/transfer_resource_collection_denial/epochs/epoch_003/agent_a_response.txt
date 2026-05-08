def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        hit_obstacle = 1 if (nx, ny) in obs else 0
        best_key = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # prefer being ahead; then closer; then deterministic by coordinates
            key = (hit_obstacle, ds - do, ds, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
        candidates.append((best_key, [dx, dy]))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0])
    return candidates[0][1]