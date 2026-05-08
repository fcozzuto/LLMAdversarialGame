def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_key = None
    for x, y in resources:
        our_d = man(sx, sy, x, y)
        opp_d = man(ox, oy, x, y)
        adv = opp_d - our_d
        key = (-adv, our_d, -x, -y)  # prefer larger adv, then closer; deterministic
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    tx, ty = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_step = (0, 0)
    best_step_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        our_d = man(nx, ny, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        adv = opp_d - our_d
        key = (-adv, our_d, dx * dx + dy * dy, dx, dy)
        if best_step_key is None or key < best_step_key:
            best_step_key = key
            best_step = (dx, dy)
    return [int(best_step[0]), int(best_step[1])]