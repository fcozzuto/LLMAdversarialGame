def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(v, lo, hi):
        if v < lo: return lo
        if v > hi: return hi
        return v

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose target resource I can reach earlier than opponent (or at least strongly favor).
    best_t = None
    best_score = -10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d_my = dist((sx, sy), (rx, ry))
        d_op = dist((ox, oy), (rx, ry))
        # Prefer resources where I'm closer; add slight bias to current proximity.
        score = (d_op - d_my) * 3 - d_my
        if score > best_score:
            best_score = score
            best_t = (rx, ry)

    # If no resources, head away from opponent toward center.
    if best_t is None:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        cx = sx - (ox - sx)  # bias away from opponent
        cy = sy - (oy - sy)
        best_t = (int(round((tx + cx) / 2.0)), int(round((ty + cy) / 2.0)))

    tx, ty = best_t

    best_move = (0, 0)
    best_move_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Avoid moving into a square that lets opponent become significantly closer to the same target.
        d_my = dist((nx, ny), (tx, ty))
        d_op = dist((ox, oy), (tx, ty))
        # Encourage immediate progress plus mild opponent denial.
        immediate = -d_my
        deny = 2 * (d_op - d_my)
        # Extra: if opponent is near my next square, slightly penalize.
        danger = - (dist((nx, ny), (ox, oy)) == 0) * 5 - (dist((nx, ny), (ox, oy)) <= 1) * 2
        score = immediate + deny + danger
        if score > best_move_score:
            best_move_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]