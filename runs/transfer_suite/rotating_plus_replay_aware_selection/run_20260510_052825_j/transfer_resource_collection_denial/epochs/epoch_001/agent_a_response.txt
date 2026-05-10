def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    self_pos = observation.get('self_position', [0, 0])
    opp_pos = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))
    if not resources:
        return [0, 0]

    sx, sy = self_pos
    ox, oy = opp_pos

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose target: minimize our distance, but prioritize resources where we're likely to arrive first.
    best = None
    for r in resources:
        rx, ry = r[0], r[1]
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Higher weight to being ahead (opponent distance). Deterministic tie-breakers.
        key = (sd - 0.8 * od, sd, -od, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    if best is None:
        return [0, 0]
    rx, ry = best[1]

    # Move one step (including diagonal/stay), avoiding obstacles if possible.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    cur_d = cheb(sx, sy, rx, ry)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, rx, ry)
        # Prefer reducing distance; if tied, prefer moves that also keep opponent further.
        opp_nd = cheb(ox, oy, rx, ry)
        # Stable tie-break: smallest nd, then lexicographically by move.
        key = (nd, -opp_nd, abs(dx) + abs(dy), dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, (dx, dy))

    if best_move is not None:
        return list(best_move[1])

    # If blocked by obstacles, try any valid (even if not reducing distance).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
    return [0, 0]