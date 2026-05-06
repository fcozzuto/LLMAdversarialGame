def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    if resources:
        # Prefer resources far from opponent; among those, go to the closest.
        tx, ty = min(resources, key=lambda r: (-dist(ox, oy, r[0], r[1]), dist(sx, sy, r[0], r[1]), r[0], r[1]))
    else:
        # Fallback: head toward center-ish.
        tx, ty = w // 2, h // 2

    best_move = [0, 0]
    best_val = None
    neighbor_op = dist(ox, oy, sx, sy) <= 1
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            d_to_t = dist(nx, ny, tx, ty)
            d_to_o = dist(nx, ny, ox, oy)
            # If close to opponent, kiting is urgent; otherwise prioritize target.
            val = (3 * d_to_o - d_to_t) if neighbor_op else (-d_to_t + 0.8 * d_to_o)
            # Small tie-breaker: avoid stepping onto resource-less "dead corners" if target is elsewhere.
            if best_val is None or val > best_val or (val == best_val and (d_to_t, -d_to_o) < (dist(sx + best_move[0], sy + best_move[1], tx, ty), -dist(sx + best_move[0], sy + best_move[1], ox, oy))):
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]