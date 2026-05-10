def choose_move(observation):
    w = int(observation.get("grid_width", 8)) or 8
    h = int(observation.get("grid_height", 8)) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    resources = list(observation.get("resources", []) or [])
    res_cells = [tuple(r) for r in resources if isinstance(r, (list, tuple)) and len(r) >= 2]

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if res_cells:
        tx, ty = min(res_cells, key=lambda p: abs(p[0]-sx) + abs(p[1]-sy))
    else:
        tx, ty = ox, oy

    best = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist_t = abs(nx - tx) + abs(ny - ty)
        dist_o = abs(nx - ox) + abs(ny - oy)
        score = -dist_t + 0.15 * dist_o + 1e-6 * (dx + 2 * dy)
        if score > best_score:
            best_score = score
            best = [int(dx), int(dy)]
    if best == [0, 0] and (sx, sy) not in obstacles:
        return [0, 0]
    return best