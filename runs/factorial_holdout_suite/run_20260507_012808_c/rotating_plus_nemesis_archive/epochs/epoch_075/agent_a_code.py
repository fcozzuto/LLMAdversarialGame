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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            moves.append((dx, dy))

    if not moves or not resources:
        return [0, 0]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Pick a resource that we reach earlier than opponent, prefer big lead.
    best_r = None
    best_key = None
    for r in resources:
        my_d = dist((sx, sy), r)
        op_d = dist((ox, oy), r)
        key = (op_d - my_d, -my_d, r[0], r[1])
        if best_key is None or key > best_key:
            best_key, best_r = key, r

    tx, ty = best_r
    # If we can step onto a resource, do it (deterministic).
    on_resource_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in resources:
            on_resource_moves.append((dx, dy))
    if on_resource_moves:
        on_resource_moves.sort()
        return list(on_resource_moves[0])

    # Otherwise, choose move that best reduces our distance to target while keeping opponent not too close.
    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        my_d2 = dist((nx, ny), (tx, ty))
        op_d2 = dist((ox, oy), (tx, ty))
        # Encourage increasing our lead; slight penalty if we get closer but opponent is also extremely near target
        score = ((op_d2 - my_d2), -my_d2, -dist((nx, ny), (ox, oy)), dx, dy)
        scored.append((score, dx, dy))
    scored.sort(reverse=True)
    return [scored[0][1], scored[0][2]]