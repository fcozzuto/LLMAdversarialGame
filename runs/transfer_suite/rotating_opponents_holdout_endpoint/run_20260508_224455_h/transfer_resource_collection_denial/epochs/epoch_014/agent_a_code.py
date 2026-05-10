def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist_m(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dx = dx if dx >= 0 else -dx
        dy = ay - by; dy = dy if dy >= 0 else -dy
        return dx + dy

    if (sx, sy) in resources:
        return [0, 0]

    best_r = None
    best_key = None
    for r in resources:
        sd = dist_m((sx, sy), r)
        od = dist_m((ox, oy), r)
        # Prefer resources we can secure first; if tied/behind, contest closest-to-them.
        key = (od - sd, -od, -sd)  # maximize
        if best_key is None or key > best_key:
            best_key = key
            best_r = r

    rx, ry = best_r if best_r is not None else (sx, sy)

    # If opponent is already much closer to nearest resource, slightly bias blocking by choosing farthest-from-opponent
    # among steps that reduce our distance to the target.
    best_step = (0, 0)
    best_step_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = dist_m((nx, ny), (rx, ry))
        no = dist_m((nx, ny), (ox, oy))  # how "central" we are relative to them (smaller is worse for blocking)
        step_key = (-ns, no)  # minimize ns, and prefer larger no (keep distance from opponent)
        if best_step_key is None or step_key > best_step_key:
            best_step_key = step_key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]