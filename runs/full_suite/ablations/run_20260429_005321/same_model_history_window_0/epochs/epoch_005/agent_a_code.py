def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    best_move = [0, 0]
    best_val = -10**18

    if resources:
        tx, ty = min(resources, key=lambda r: cheb(sx, sy, r[0], r[1]))
    else:
        tx, ty = (gw - 1 - sx), (gh - 1 - sy)

    move_order = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        nx, ny = clamp(nx, 0, gw - 1), clamp(ny, 0, gh - 1)
        if (nx, ny) in obstacles:
            val = -10**12
        else:
            dist_to_target = cheb(nx, ny, tx, ty)
            dist_to_opp = cheb(nx, ny, ox, oy)
            on_resource = 1 if [nx, ny] in resources or (nx, ny) in set(map(tuple, resources)) else 0
            # Prefer decreasing target distance, avoid opponent, and prefer corners/space slightly.
            val = -dist_to_target + 25 * on_resource + 0.02 * dist_to_opp
            # If target is already near, prioritize collecting by looking for adjacent resource.
            if resources:
                adj = 0
                for rx, ry in resources:
                    if abs(rx - nx) <= 0 and abs(ry - ny) <= 0:
                        adj += 2
                    elif abs(rx - nx) <= 1 and abs(ry - ny) <= 1:
                        adj += 1
                val += 3 * adj
            # Small bias to keep moving (except when blocked).
            if (dx, dy) != (0, 0):
                val += 0.01
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move