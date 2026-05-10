def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort(key=lambda d: (-(d[0] == 0 and d[1] == 0), 0))  # keep deterministic preference to stay last

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: man(c[0], c[1], ox, oy))
        best = (None, -10**9)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            score = man(nx, ny, ox, oy) - man(nx, ny, tx, ty) * 0.2
            if score > best[1]:
                best = ((dx, dy), score)
        return [best[0][0], best[0][1]] if best[0] is not None else [0, 0]

    # Pick the move that maximizes guaranteed collection advantage in one step
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        worst_case = 10**9
        # Prefer moves that improve my lead over opponent for some resource
        best_adv_for_move = -10**9
        tie_break = 0
        for rx, ry in resources:
            d_me = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            adv = d_op - d_me  # positive means I'm closer right now
            if adv > best_adv_for_move:
                best_adv_for_move = adv
            # ensure not choosing move that gives opponent an immediate closer alternative
            gap = adv
            if gap < worst_case:
                worst_case = gap
            tie_break += -d_me
        # Strongly favor grabbing resources where I'm ahead; penalize moves that make opponent more likely
        val = best_adv_for_move * 1000 + worst_case - tie_break * 0.01
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]