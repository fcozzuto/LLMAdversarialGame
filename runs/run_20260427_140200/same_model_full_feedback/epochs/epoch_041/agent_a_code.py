def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # If no immediate resources, head toward the nearest known empty area by using resource heuristic (centers).
    center = (w // 2, h // 2)

    best_move = [0, 0]
    best_val = -10**18

    # Precompute current min distances to make tie-breaking stable
    cur_to_center = md((sx, sy), center)
    cur_best_res = 10**9
    for r in resources:
        cur_best_res = min(cur_best_res, md((sx, sy), r))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        self_pos = (nx, ny)
        val = 0

        if resources:
            # Choose resource that maximizes advantage (opp farther than us), with diminishing by distance.
            # Also add a small term to prevent chasing a single far resource.
            best_for_move = -10**18
            for r in resources:
                ds = md(self_pos, r)
                do = md((ox, oy), r)

                # Approx "initiative": how much closer we are compared to opponent
                adv = do - ds  # positive means we are closer now
                # Encourage grabbing nearby resources first
                near = -ds
                # Strongly discourage moves that allow opponent to be closer after their next step
                # (roughly: compare our ds to their do assuming similar movement)
                contested = adv * 3 - ds * 0.7

                # If opponent is already closer (adv negative), deprioritize but still consider if very near.
                score = contested + near
                if score > best_for_move:
                    best_for_move = score
            val += best_for_move
        else:
            # No resources visible: drift toward center to improve future acquisition chances deterministically
            val += -md(self_pos, center)

        # Mild anti-oscillation / stability: prefer not increasing distance to best reachable resource
        if resources and cur_best_res < 10**9:
            new_best = 10**9
            for r in resources:
                new_best = min(new_best, md(self_pos, r))
            val += (cur_best_res - new_best) * 0.5

        # Deterministic tie-break: prefer smaller dx, then smaller dy, then no-op
        tie = (abs(dx), abs(dy), 0 if (dx == 0 and dy == 0) else 1)
        val -= tie[0] * 1e-3 + tie[1] * 1e-6 + tie[2] * 1e-9

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]