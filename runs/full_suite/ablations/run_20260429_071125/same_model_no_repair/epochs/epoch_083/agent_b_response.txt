def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Strategy: for each move, maximize the best "steal advantage" across resources.
    # New twist vs basic greedy: prefer moves that (a) reduce the leader's advantage and
    # (b) improve distance to the next contested resource, not just the currently best one.
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_center = cheb(nx, ny, cx, cy)  # uses float, but cheb handles via arithmetic; ok for heuristic
        local_best = -10**18

        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)

            # Advantage if we can be closer than opponent to this resource
            adv = op_d - my_d

            # "Contest pressure": if opponent is much closer, we want to reduce their lead.
            # Also slightly favor nearer arrival time for contested targets.
            pressure = 0
            if adv < 0:
                pressure = 0.7 * (-adv)  # reducing negative adv matters
            else:
                pressure = 0.2 * adv

            # Additional deterministic tie-break: prefer targets that opponent is not already winning decisively for.
            # (smaller op_d is more dangerous, so we subtract it lightly)
            risk = 0.05 * op_d

            # Combine: want large adv, good pressure, low risk, and avoid moving too far from center late-game.
            val = adv * 10 + pressure - risk - 0.03 * my_center

            if val > local_best:
                local_best = val

        if local_best > best_val:
            best_val = local_best
            best_move = (dx, dy)
        elif local_best == best_val:
            # Deterministic tie-break: prefer staying when equal; then smallest |dx|+|dy|
            if best_move != (0, 0) and (dx, dy) == (0, 0):
                best_move = (dx, dy)
            else:
                if abs(dx) + abs(dy) < abs(best_move[0]) + abs(best_move[1]):
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]