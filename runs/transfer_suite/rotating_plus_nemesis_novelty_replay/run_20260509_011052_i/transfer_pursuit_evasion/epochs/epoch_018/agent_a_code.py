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
    # Evader likely aims for corner farthest from pursuer
    corner = max(corners, key=lambda c: abs(sx - c[0]) + abs(sy - c[1]))

    # Block along the wall corresponding to evader's target corner
    if corner[0] in (0, w - 1):
        block = (corner[0], oy)
    else:
        block = (ox, corner[1])

    # If already near a wall, tighten block to corner-adjacent coordinate
    wall_dist = min(ox, w - 1 - ox, oy, h - 1 - oy)
    if wall_dist <= 2:
        if corner[0] in (0, w - 1):
            block = (corner[0], corner[1] if corner[1] in (0, h - 1) else oy)
        else:
            block = (corner[0], corner[1])

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_opp = max(abs(nx - ox), abs(ny - oy))  # smaller is better
        d_block = abs(nx - block[0]) + abs(ny - block[1])  # smaller is better

        # Alignment: move toward the direction from us to the evader's target corner
        mx = 0 if corner[0] == sx else (1 if corner[0] > sx else -1)
        my = 0 if corner[1] == sy else (1 if corner[1] > sy else -1)
        align = dx * mx + dy * my

        # Priority: catch, then cut off corner escape, then align
        score = (-1000 * d_opp) + (-5 * d_block) + (2 * align)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move