def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)
    role = observation.get("self_role", "pursuer")
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if role == "pursuer":
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obs:
                continue
            v = dist(nx, ny, ox, oy)
            if best_val is None or v < best_val:
                best_val = v
                best_move = [dx, dy]
        if best_val is None:
            best_move = [0, 0]
        return best_move

    # evader/runner: move to maximize distance, bias toward farthest corner
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda p: dist(p[0], p[1], ox, oy))
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        v = dist(nx, ny, ox, oy) * 100 - dist(nx, ny, far_corner[0], far_corner[1])
        if best_val is None or v > best_val:
            best_val = v
            best_move = [dx, dy]
    if best_val is None:
        best_move = [0, 0]
    return best_move