def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r is not None and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return x < 0 or y < 0 or x >= w or y >= h or (x, y) in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    # Pick a deterministic target: closest by chebyshev, tie by coordinates.
    best_t = None
    best_td = None
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        if best_t is None or d < best_td or (d == best_td and (rx, ry) < best_t):
            best_t = (rx, ry)
            best_td = d
    tx, ty = best_t

    # Evaluate each move by relative progress toward target and distancing from opponent.
    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        my_d = cheb(nx, ny, tx, ty)
        op_d = cheb(ox, oy, tx, ty)

        # Encourage decreasing my distance; if I'm not winning target race, value slowing opponent.
        # Also add slight penalty if moving closer to opponent (avoid contesting directly).
        my_to_op_next = cheb(nx, ny, ox, oy)
        op_to_op_curr = cheb(ox, oy, sx, sy)  # deterministic scale only

        score = (-my_d) + 0.35 * op_d - 0.08 * my_to_op_next + 0.01 * (my_to_op_next - op_to_op_curr)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            # Deterministic tie-breaker: prefer lexicographically smallest move delta.
            if (dx, dy) < (best_move[0], best_move[1]):
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]