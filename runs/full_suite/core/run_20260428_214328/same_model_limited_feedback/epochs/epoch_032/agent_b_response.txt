def choose_move(observation):
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((x, y) for x, y in obstacles)
    if not resources:
        return [0, 0]

    def nearest_dist(x, y):
        best = None
        for rx, ry in resources:
            dx, dy = rx - x, ry - y
            d = dx * dx + dy * dy
            if best is None or d < best:
                best = d
        return best if best is not None else 0

    best_move = [0, 0]
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obs_set:
                continue
            move_score = 0
            # If we can step onto a resource, heavily prefer it
            if (nx, ny) in set((x, y) for x, y in resources):
                move_score += 10_000
            # Prefer minimizing distance to nearest resource
            move_score -= nearest_dist(nx, ny)
            # Prefer being farther from opponent to reduce contention
            odx, ody = ox - nx, oy - ny
            move_score += (odx * odx + ody * ody) * 0.001
            if best_score is None or move_score > best_score:
                best_score = move_score
                best_move = [dx, dy]
    return best_move