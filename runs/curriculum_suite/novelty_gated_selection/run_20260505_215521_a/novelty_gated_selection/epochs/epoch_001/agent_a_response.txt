def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obst = set((p[0], p[1]) for p in obstacles)
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    if resources:
        tx, ty = min(resources, key=lambda p: ( (p[0]-sx)*(p[0]-sx) + (p[1]-sy)*(p[1]-sy), p[0], p[1] ))
    else:
        tx, ty = ox, oy

    moves = [(0,0), (1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
    best = None
    best_d = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        if best is None or d < best_d or (d == best_d and (dx, dy) < best):
            best_d = d
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]