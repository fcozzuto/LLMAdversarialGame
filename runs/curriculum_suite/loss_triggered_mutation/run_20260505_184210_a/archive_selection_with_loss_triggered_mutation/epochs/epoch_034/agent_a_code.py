def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    def best_target_for_pos(px, py):
        best_adv = -10**9
        best_dist = 10**9
        best = (px, py)
        for rx, ry in resources:
            ds = abs(px - rx) + abs(py - ry)
            do = abs(ox - rx) + abs(oy - ry)
            adv = do - ds  # positive means we are closer
            if adv > best_adv or (adv == best_adv and ds < best_dist):
                best_adv = adv
                best_dist = ds
                best = (rx, ry)
        return best

    # Score candidate moves by resulting target advantage and closeness
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        tx, ty = best_target_for_pos(nx, ny)
        ds = abs(nx - tx) + abs(ny - ty)
        do = abs(ox - tx) + abs(oy - ty)
        adv = do - ds
        # Additional tie-break: move toward the chosen target deterministically
        step_benefit = -((tx - nx) != 0) * 0  # kept deterministic but neutral
        score = adv * 1000 - ds + step_benefit
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]