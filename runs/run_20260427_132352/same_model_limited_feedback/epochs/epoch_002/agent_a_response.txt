def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    def d(a, b, c, d0):
        return abs(a - c) + abs(b - d0)

    # Pick a target resource where we are relatively closer than the opponent
    best_t = None
    best_val = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        md = d(sx, sy, rx, ry)
        od = d(ox, oy, rx, ry)
        val = (od - md) * 3 - md  # strongly prefer resources we can reach earlier
        # slight preference for nearer overall in ties
        if val > best_val:
            best_val = val
            best_t = (rx, ry)

    if best_t is None:
        # No usable resources: drift toward center, but keep safe from obstacles
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best_t = (int(tx), int(ty))

    tx, ty = best_t

    # Evaluate each move by progress to target and safety/threat considerations
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        nx = clamp(nx, 0, w - 1)
        ny = clamp(ny, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        my_to_t = d(nx, ny, tx, ty)
        opp_to_t = d(ox, oy, tx, ty)
        # Prefer reducing distance to target and maintaining relative advantage
        score = -my_to_t + (opp_to_t - my_to_t) * 2

        # Obstacle/edge "crowding" penalty: avoid moving into corners too often
        edge_pen = 0
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            edge_pen = 0.5
        score -= edge_pen

        # Mild repulsion from opponent to reduce immediate contests near our path
        score -= 0.25 * d(nx, ny, ox, oy)

        # Small preference for staying if equally good (deterministic tie-break)
        if score > best_score or (score == best_score and (dx, dy) == (0, 0)):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]