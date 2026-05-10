def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corner = min(corners, key=lambda c: abs(ox - c[0]) + abs(oy - c[1]))

    def adj_obs(x, y):
        # prefer being near obstacles to help wall-running style control
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            if (x + dx, y + dy) in obstacles:
                return 1
        return 0

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_opp = max(abs(nx - ox), abs(ny - oy))  # diagonal pursuit (captures only if exact)
        d_corner = abs(nx - corner[0]) + abs(ny - corner[1])
        d_opp_to_corner = abs(ox - corner[0]) + abs(oy - corner[1])
        # primary: get closer to opponent; secondary: cornering; tertiary: obstacle-adjacency
        val = (d_opp, 0.35 * d_corner + 0.1 * d_opp_to_corner - 0.05 * adj_obs(nx, ny), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [int(dx), int(dy)]