def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corner = min(corners, key=lambda c: abs(ox - c[0]) + abs(oy - c[1]))

    # Choose a "blocking" point on the wall the evader is heading toward
    if corner[0] in (0, w - 1):
        block = (corner[0], oy)
    else:
        block = (ox, corner[1])

    # If opponent is already in/near a boundary, bias blocking more strongly
    wall_dist = min(ox, w - 1 - ox, oy, h - 1 - oy)
    near_wall = 1 if wall_dist <= 2 else 0

    best = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # primary: reduce pursuit distance (Chebyshev since moves are 8-dir)
        d_opp = max(abs(nx - ox), abs(ny - oy))

        # secondary: reduce distance to blocking point to cut off corner escapes
        d_block = abs(nx - block[0]) + abs(ny - block[1])

        # tertiary: when close to corner, prioritize moving along the wall direction
        along_wall_target = corner[0] if corner[0] in (0, w - 1) else corner[1]
        if corner[0] in (0, w - 1):
            wall_line_dist = abs(nx - along_wall_target)
        else:
            wall_line_dist = abs(ny - along_wall_target)

        # obstacle adjacency penalty to avoid getting stuck
        adj_obs = 0
        for ax, ay in ((1,0),(-1,0),(0,1),(0,-1)):
            if (nx + ax, ny + ay) in obstacles:
                adj_obs = 1
                break

        score = -d_opp * 1000 - d_block * (180 + 120 * near_wall) - wall_line_dist * (90 + 90 * near_wall) - adj_obs * 25
        # small preference to not stay still if scores tie
        if (dx, dy) != (0, 0):
            score += 1
        if score > best_score:
            best_score = score
            best = [dx, dy]
    return best