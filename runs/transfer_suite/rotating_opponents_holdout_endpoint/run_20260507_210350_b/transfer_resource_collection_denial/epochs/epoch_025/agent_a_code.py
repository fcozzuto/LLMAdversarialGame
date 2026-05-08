def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    if not resources:
        tx, ty = ((w - 1, 0) if (sx + sy) % 2 == 0 else (0, h - 1))
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    def obstacle_pen(x, y):
        p = 0
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d == 0:
                return 10**9
            if d == 1:
                p += 3
            elif d == 2:
                p += 1
        return p

    best = (0, 0, -10**18)  # dx,dy,score
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Choose the resource that gives best immediate advantage from (nx,ny)
        best_res = -10**18
        best_dist = 10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer
            # Encourage quick collection and discourages long detours; deterministic tie-breaks
            val = adv * 100 - ds * 2 + (0 if (nx == rx and ny == ry) else -1)
            if val > best_res or (val == best_res and ds < best_dist):
                best_res = val
                best_dist = ds

        # If we can step onto a resource, prioritize strongly
        on_resource = 1 if (nx, ny) in resources else 0
        score = best_res + on_resource * 10**6 - obstacle_pen(nx, ny)

        if score > best[2] or (score == best[2] and (dx, dy) < (best[0], best[1])):
            best = (dx, dy, score)

    return [best[0], best[1]]