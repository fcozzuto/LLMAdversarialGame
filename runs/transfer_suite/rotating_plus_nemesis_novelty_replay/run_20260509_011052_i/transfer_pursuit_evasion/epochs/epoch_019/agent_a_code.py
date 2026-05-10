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

    # Estimate opponent "escape direction" towards the nearest corner
    ex = 0 if ox == corner[0] else (1 if ox > corner[0] else -1)
    ey = 0 if oy == corner[1] else (1 if oy > corner[1] else -1)
    px, py = ox + ex, oy + ey
    if not (0 <= px < w and 0 <= py < h):
        px, py = ox, oy

    # Block the corresponding wall line using the projected position
    if corner[0] in (0, w - 1):
        block = (corner[0], py)
    else:
        block = (px, corner[1])

    wall_dist = min(ox, w - 1 - ox, oy, h - 1 - oy)
    near_wall = 1 if wall_dist <= 2 else 0

    best = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_opp = max(abs(nx - ox), abs(ny - oy))  # Chebyshev
        score = -3.0 * d_opp
        if nx == ox and ny == oy:
            score += 1000.0
        # Cut off corner entry/escape line
        d_block = abs(nx - block[0]) + abs(ny - block[1])
        score += -(1.8 + 1.0 * near_wall) * d_block

        # When not near a wall, prefer direct approach slightly
        d_corner = abs(nx - corner[0]) + abs(ny - corner[1])
        score += -(0.2 if near_wall else 0.8) * d_corner

        # Mild tie-break: prefer moves that reduce Manhattan distance to opponent
        d_man = abs(nx - ox) + abs(ny - oy)
        score += -0.01 * d_man

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]