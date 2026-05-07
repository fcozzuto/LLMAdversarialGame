def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if (sx, sy) in resources:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    my = (sx, sy)
    opp = (ox, oy)

    my_closer = []
    for t in resources:
        dm = man(my, t)
        do = man(opp, t)
        if dm < do:
            my_closer.append((t, dm, do))
    pool = my_closer if my_closer else [(t, man(my, t), man(opp, t)) for t in resources]

    # Choose target: prefer being closer than opponent; if none, race closest.
    best_t = None
    best_key = None
    for t, dm, do in pool:
        lead = do - dm
        # Key: maximize lead; then minimize our distance; then deterministic by coords
        key = (-lead, dm, t[0], t[1])  # negative lead -> smaller is better when lead larger
        if best_key is None or key < best_key:
            best_key = key
            best_t = t

    tx, ty = best_t

    # One-step greedy move towards target with obstacle and bounds avoidance.
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_d = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d = man((nx, ny), (tx, ty))
            if best_d is None or d < best_d:
                best_d = d
                best_move = [dx, dy]
    return best_move