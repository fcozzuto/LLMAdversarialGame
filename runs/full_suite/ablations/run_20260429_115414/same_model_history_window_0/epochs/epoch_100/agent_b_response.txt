def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    # Candidate moves (including stay), avoid obstacles if possible
    dirs = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    # If no resources, head toward farthest corner away from opponent deterministically
    if not resources:
        tx = 0 if ox >= w / 2 else w - 1
        ty = 0 if oy >= h / 2 else h - 1
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        dx = dx if dx in (-1, 0, 1) else 0
        dy = dy if dy in (-1, 0, 1) else 0
        return [dx, dy]

    best = None
    # Evaluate each move by targeting a resource where we have relative advantage over opponent
    for dx, dy, nx, ny in candidates:
        best_adv = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            # If we land on resource, prioritize strongly
            our_d = dist((nx, ny), (rx, ry))
            opp_d = dist((ox, oy), (rx, ry))
            # Smaller is better: maximize (opp_d - our_d), plus tiny deterministic tie-break
            adv = (opp_d - our_d) * 1000 + (0 if our_d == 0 else -our_d)
            tieb = (opp_d - our_d, -our_d, rx, ry)
            if best_adv is None or (adv, tieb) > best_adv:
                best_adv = (adv, tieb)
        # Additional anti-stall: prefer moves that reduce our distance to the best resource under tie-break
        overall = best_adv[0]
        overall_t = best_adv[1]
        key = (overall, overall_t, -abs(dx) - abs(dy), nx, ny, dx, dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1]