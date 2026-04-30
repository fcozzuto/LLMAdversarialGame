def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick a target that we can reach quickly while staying relatively far from opponent
    best_t = None
    best_val = None
    for rx, ry in resources:
        d_us = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        val = (-d_us * 10) + (d_op * 2)  # maximize reach + distance advantage
        if best_val is None or val > best_val or (val == best_val and (rx, ry) < best_t):
            best_val = val
            best_t = (rx, ry)

    if best_t is None:
        # No resources visible: drift toward center while avoiding moving closer to opponent too much
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = cx, cy
    else:
        tx, ty = best_t

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Evaluate moves by closeness to target, occupancy, and not enabling opponent
    best_m = (0, 0)
    best_s = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        on_resource = 1 if (nx, ny) in obstacles else 0  # obstacles shouldn't be reachable, keep deterministic
        new_to_t = cheb(nx, ny, tx, ty)
        new_to_op = cheb(nx, ny, ox, oy)

        # If we can move onto a resource, heavily prefer it.
        if (nx, ny) in resources:
            s = 10_000 - new_to_t - cheb(nx, ny, tx, ty) + new_to_op * 0.5
        else:
            # Encourage faster approach and keep distance from opponent.
            s = (-new_to_t * 20) + (new_to_op * 1.5) - cheb(ox, oy, tx, ty) * 0.05

        # Tie-break deterministically by move ordering
        if best_s is None or s > best_s or (s == best_s and (dx, dy) < best_m):
            best_s = s
            best_m = (dx, dy)

    dx, dy = best_m
    return [int(dx), int(dy)]