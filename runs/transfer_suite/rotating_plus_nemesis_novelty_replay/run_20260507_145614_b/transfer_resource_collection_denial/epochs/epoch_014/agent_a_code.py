def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_r = None
    best_key = None
    for rx, ry in resources:
        if not valid(rx, ry):
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        closer = ds - do
        # Prefer resources I can beat; otherwise prefer least-bad by how much opponent is closer.
        # Key: (beat_flag, closer, -ds, rx, ry) to get deterministic min.
        beat_flag = 0 if ds <= do else 1
        key = (beat_flag, abs(closer), -ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_r

    best_step = (0, 0)
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds_new = cheb(nx, ny, tx, ty)
        do_curr_to = cheb(ox, oy, tx, ty)
        # If we can't win target, slightly prefer steps that worsen opponent's relative access.
        rel = ds_new - do_curr_to
        key = (0 if ds_new <= do_curr_to else 1, abs(rel), ds_new, dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]