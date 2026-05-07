def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # If we can grab a resource this turn, prioritize it strongly.
        immediate = 1 if (nx, ny) in obstacles else 0  # should be 0 due to valid(), kept deterministic
        val = 0
        if (nx, ny) in resources:
            val += 100000

        # Otherwise, choose a target where we have distance advantage over opponent.
        # Also prefer resources with different y-band from opponent (anti-sweep_rows competition).
        best_target = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            advantage = (do - ds)  # positive means we're closer than opponent
            y_sep = abs(ry - oy)
            t = advantage * 1000 - ds * 5 + y_sep * 2
            if t > best_target:
                best_target = t

        val += best_target
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]