def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0

    def move_score(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            return None
        # If already on a resource, just stay competitive
        best = -10**9
        for rx, ry in resources if resources else []:
            my_d = man(nx, ny, rx, ry)
            op_d = man(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; add small tie-break for being nearer
            val = (op_d - my_d) * 1000 - my_d
            # Encourage not moving away from the target resource too slowly
            val -= int((my_d - man(sx, sy, rx, ry)) > 0) * 50
            if val > best:
                best = val
        if resources:
            # Also include slight center bias to avoid oscillations on equal targets
            best += -int(abs(nx - cx) + abs(ny - cy))
            return best
        # No resources visible: head toward opponent corner to deny
        # (deterministic fallback)
        return -man(nx, ny, ox, oy) * 10 - (abs(nx - cx) + abs(ny - cy))

    candidates = []
    for dx, dy in moves:
        sc = move_score(dx, dy)
        if sc is not None:
            candidates.append((sc, dx, dy))
    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]