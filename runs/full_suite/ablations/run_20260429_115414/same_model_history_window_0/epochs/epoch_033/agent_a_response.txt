def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    if resources:
        # Nearest resource to us, deterministic tie-break by (x,y)
        tx, ty = min(((rx, ry) for rx, ry in resources), key=lambda p: (dist2(sx, sy, p[0], p[1]), p[0], p[1]))
    else:
        # No resources: drift toward center and keep distance from opponent
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = (cx, cy)

    best_moves = []
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            d = dist2(nx, ny, tx, ty)
            # Prefer approaching target; then prefer away from opponent
            od = dist2(nx, ny, ox, oy)
            score = (d, -od, abs(dx), abs(dy), dx, dy)
            if best_score is None or score < best_score:
                best_score = score
                best_moves = [(dx, dy)]
            elif score == best_score:
                best_moves.append((dx, dy))

    if best_moves:
        return list(min(best_moves, key=lambda m: (m[0], m[1])))
    # If trapped by obstacles (should be rare), allow any in-bounds move minimizing distance
    best_moves = []
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            d = dist2(nx, ny, tx, ty)
            score = (d, abs(dx), abs(dy), dx, dy)
            if best_score is None or score < best_score:
                best_score = score
                best_moves = [(dx, dy)]
            elif score == best_score:
                best_moves.append((dx, dy))
    return list(min(best_moves, key=lambda m: (m[0], m[1])))