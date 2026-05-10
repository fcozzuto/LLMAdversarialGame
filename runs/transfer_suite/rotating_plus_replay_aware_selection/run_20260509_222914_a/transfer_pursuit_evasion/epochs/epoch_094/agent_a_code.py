def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("fugitive" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def free_nbr_count(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = man(nx, ny, ox, oy)
        fn = free_nbr_count(nx, ny)
        center_bias = -((nx - (w - 1) / 2) ** 2 + (ny - (h - 1) / 2) ** 2) * 1e-6

        if is_evader:
            # Run to maximize distance; keep from corners that are tight; prefer locally open cells.
            corner_pref = 0
            if (nx, ny) in {(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)}:
                corner_pref = 0.05
            key = (d, fn, corner_pref, center_bias, -dx * 0.001 - dy * 0.001)
        else:
            # Pursue while avoiding traps: minimize distance, break ties by openness.
            key = (-d, fn, center_bias, dx * 0.001 + dy * 0.001)

        if best is None or key > best_key:
            best, best_key = [dx, dy], key

    # If all moves blocked, stay still.
    return best if best is not None else [0, 0]