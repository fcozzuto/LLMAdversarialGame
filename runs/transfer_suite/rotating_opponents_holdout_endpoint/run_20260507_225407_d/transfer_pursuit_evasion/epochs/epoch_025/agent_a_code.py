def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None:
            continue
        obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("pursuit" in self_role and "evasion" not in self_role) or ("pursue" in self_role)
    is_evader = ("evader" in self_role) or ("evasion" in self_role) or ("escape" in self_role)
    if not is_pursuer and not is_evader:
        is_pursuer = ("pursuer" in opp_role)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    d_now = abs(ox - sx) + abs(oy - sy)

    if is_evader:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best_corner = max(corners, key=lambda c: abs(ox - c[0]) + abs(oy - c[1]))
        tx, ty = best_corner
        best_key = None
        best_val = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d_next = abs(ox - nx) + abs(oy - ny)
            corner_push = abs(tx - nx) + abs(ty - ny)
            # maximize distance to pursuer; then maximize distance to target corner (staying far)
            val = (d_next, corner_push)
            key = (-val[0], -val[1], dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_val = [dx, dy]
        return best_val if best_val is not None else [0, 0]

    # pursuer policy: greedy reduce manhattan distance; slight preference to keep movement monotone toward opponent
    best_key = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d_next = abs(ox - nx) + abs(oy - ny)
        gain = d_now - d_next
        # bias: align with opponent direction and avoid stepping away if same distance
        align = 0
        if dx != 0:
            align += 1 if (ox - sx) * dx > 0 else 0
        if dy != 0:
            align += 1 if (oy - sy) * dy > 0 else 0
        key = (-gain, -align, abs(dx), abs(dy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move