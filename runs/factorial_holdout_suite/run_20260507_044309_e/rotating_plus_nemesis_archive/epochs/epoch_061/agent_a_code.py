def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate how quickly we can secure a resource compared to opponent.
        # Key: minimize advantage (self_distance - opp_distance). Then minimize self distance.
        min_adv = None
        min_self = None
        for rx, ry in resources:
            dself = man(nx, ny, rx, ry)
            dopp = man(ox, oy, rx, ry)
            adv = dself - dopp
            if min_adv is None or adv < min_adv or (adv == min_adv and dself < min_self):
                min_adv = adv
                min_self = dself

        # Prefer going for wins sooner; break ties deterministically by dx,dy order via moves list.
        key = (min_adv, min_self, abs(nx - ox) + abs(ny - oy))
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]