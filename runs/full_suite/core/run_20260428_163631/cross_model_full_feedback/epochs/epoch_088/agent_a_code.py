def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    me = (sx, sy)
    op = (ox, oy)

    # If resources exist: pick a move that makes us relatively closer to a resource than the opponent,
    # with fallback to distancing from opponent while still moving toward best available resource.
    best = legal[0]
    best_val = -10**18
    for dx, dy in legal:
        pos = (sx + dx, sy + dy)
        d_to_op = dist(pos, op)

        if resources:
            # Evaluate best resource after this move by relative advantage.
            best_r_adv = -10**18
            best_r_d = 10**18
            for r in resources:
                d_me = dist(pos, r)
                d_op = dist(op, r)
                adv = d_op - d_me  # higher is better: we are closer than opponent
                if adv > best_r_adv or (adv == best_r_adv and d_me < best_r_d):
                    best_r_adv = adv
                    best_r_d = d_me
            # If we can secure something (adv > 0), prioritize it strongly; else hedge by increasing distance to opponent.
            val = 4.0 * best_r_adv - 0.05 * best_r_d + (0.15 if best_r_adv <= 0 else 0.0) * d_to_op
        else:
            # No resources: just move to increase distance from opponent.
            val = d_to_op

        # Small deterministic tie-breaker: prefer moves with smaller dx, then smaller dy.
        val += 1e-6 * (-(dx * 3 + dy))
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]