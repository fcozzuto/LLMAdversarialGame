def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        our_min = 10**9
        opp_min = 10**9
        our_to_closest = 10**9
        for rx, ry in resources:
            d_ou = cheb(nx, ny, rx, ry)
            if d_ou < our_min:
                our_min = d_ou
                our_to_closest = d_ou
            d_op = cheb(ox, oy, rx, ry)
            if d_op < opp_min:
                opp_min = d_op

        # Prefer improving capture odds vs opponent; slight preference for shorter own distance.
        score = (opp_min - our_min) * 1000 - our_to_closest
        # Tie-break deterministically: prefer smaller movement delta, then lexicographic.
        move_cost = abs(dx) + abs(dy) - (1 if dx != 0 and dy != 0 else 0)
        key = (score, -move_cost, -nx, -ny)
        if best is None or key > best_key:
            best = (dx, dy)
            best_key = key

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]