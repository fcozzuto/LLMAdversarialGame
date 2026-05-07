def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = None

    # Different from naive "go nearest": aim to deny by maximizing lead over the opponent
    # for the single most contestable resource after the move.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        local_best_adv = None
        local_best_us = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)
            adv = opd - myd  # >0 means we can reach no later than opponent
            us = myd
            if local_best_adv is None or adv > local_best_adv or (adv == local_best_adv and us < local_best_us):
                local_best_adv = adv
                local_best_us = us

        # If we can secure a lead, strongly prefer it; otherwise minimize how badly we lag.
        val = (0, 0, 0)
        if local_best_adv > 0:
            val = (2, local_best_adv, -local_best_us)
        elif local_best_adv == 0:
            val = (1, 0, -local_best_us)
        else:
            # negative: less negative is better
            val = (0, local_best_adv, -local_best_us)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]