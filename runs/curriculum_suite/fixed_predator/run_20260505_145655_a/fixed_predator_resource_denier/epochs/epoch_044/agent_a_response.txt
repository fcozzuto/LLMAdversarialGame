def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cell_score(cx, cy):
        best_adv = -10**18
        best_r = None
        for rx, ry in resources:
            selfd = abs(cx - rx) + abs(cy - ry)
            oppd = abs(ox - rx) + abs(oy - ry)
            adv = (oppd - selfd) * 10 - selfd
            if adv > best_adv:
                best_adv = adv
                best_r = (rx, ry)
        if best_r is None:
            return -10**18
        rx, ry = best_r
        selfd = abs(cx - rx) + abs(cy - ry)
        oppd = abs(ox - rx) + abs(oy - ry)
        # If opponent is already ahead, emphasize denial by heading to the contested resource anyway.
        deny = -max(0, selfd - oppd) * 3
        # Small tie-break toward moving closer to best target.
        clos = -selfd
        return best_adv + deny + clos

    best = None
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = cell_score(nx, ny)
        if best is None or sc > best_sc or (sc == best_sc and (dx, dy) < (best[0], best[1])):
            best_sc = sc
            best = (dx, dy)

    return [best[0], best[1]]