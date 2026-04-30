def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles or not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Heuristic: for each candidate move, evaluate advantage over the best "contested" resource.
    # advantage = (op_dist - self_dist), higher is better; tie-break with smaller self_dist.
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        local_best_adv = -10**18
        local_best_sd = 10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            # Prefer resources where we are at least as close and especially where we can "race" them.
            if adv > local_best_adv or (adv == local_best_adv and sd < local_best_sd):
                local_best_adv = adv
                local_best_sd = sd

        # Extra bias: if opponent is closer overall, reduce self distance to the closest resource.
        closest_sd = min(man(nx, ny, rx, ry) for rx, ry in resources)
        closest_od = min(man(ox, oy, rx, ry) for rx, ry in resources)

        score = local_best_adv * 100 - closest_sd + (closest_od - closest_sd) * 5
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]