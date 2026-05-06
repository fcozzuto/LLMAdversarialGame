def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    res = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if (rx, ry) not in obstacles:
                res.append((rx, ry))

    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Predict opponent's immediate greedy target (safe_collector-like)
    opp_target = min(res, key=lambda r: (man(ox, oy, r[0], r[1]), r[0], r[1]))

    # If we can take it now, do it.
    for r in res:
        if r == (sx, sy):
            return [0, 0]

    best_dxdy = (0, 0)
    best_val = -10**18

    # Small repulsion from obstacles to avoid getting stuck near them
    def obs_pen(x, y):
        p = 0
        for (oxb, oyb) in obstacles:
            d = man(x, y, oxb, oyb)
            if d == 0:
                return 10**9
            if d <= 2:
                p += (3 - d) * 5
        return p

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_d = man(nx, ny, opp_target[0], opp_target[1])
        opp_d = man(ox, oy, opp_target[0], opp_target[1])

        # Race control: maximize advantage over opponent on predicted target
        v = (opp_d - my_d) * 250 - my_d

        # If move also reduces distance to other resources where opponent is closer,
        # slightly discourage because safe_collector will grab them; focus on contest target.
        nearest_to_opp_else = min(res, key=lambda r: (man(ox, oy, r[0], r[1]), r[0], r[1]))
        if nearest_to_opp_else != opp_target:
            v -= man(nx, ny, nearest_to_opp_else[0], nearest_to_opp_else[1]) * 1

        # Obstacle avoidance
        v -= obs_pen(nx, ny)

        # Tie-break deterministically: prefer moves that change both coords (diagonal) then lowest dx,dy
        v += (1 if dx != 0 and dy != 0 else 0) * 0.1
        key = (v, -dx, -dy)  # deterministic preference via sign ordering

        if key[0] > best_val:
            best_val = key[0]
            best_dxdy = (dx, dy)

        elif key[0] == best_val:
            # Deterministic tie-breaker
            if (-dx, -dy) < (-best_dxdy[0], -best_dxdy[1]):
                best_dxdy = (dx, dy)

    dx, dy = best_dxdy
    return [int(dx), int(dy)]