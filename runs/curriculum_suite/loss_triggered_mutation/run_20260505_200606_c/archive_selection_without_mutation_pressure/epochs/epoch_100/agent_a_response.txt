def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            r = (p[0], p[1])
            if r not in obstacles:
                resources.append(r)
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Intercept policy: prefer resources where we can arrive earlier than opponent.
    # If resources are scarce, bias toward closest capture.
    remaining = observation.get("remaining_resource_count")
    scarcity = 1.0
    if isinstance(remaining, int) and remaining <= 4:
        scarcity = 1.35

    best = None
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        v = -0.08 * (abs(dx) + abs(dy))  # slight preference for calmer moves
        nearest_opp = 10**9

        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # want ds - do to be small/negative; also encourage short ds
            gap = ds - do
            # primary: intercept earliest; secondary: progress
            score = (-2.2 * gap) - 0.35 * ds
            v += score / (1 + ds)

            # track closest opponent pressure to add a global deterrent
            if do < nearest_opp:
                nearest_opp = do

        # extra pressure if opponent is very near our predicted best region
        v += scarcity * (-0.08 * nearest_opp)

        if v > best_val:
            best_val = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]