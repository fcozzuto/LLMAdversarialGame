def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    best = (None, -10**18, 10**18)  # (move, score, mindist_to_any)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        opp_step_pen = 0
        my_best = 10**18
        score_move = -10**18

        for i, (rx, ry) in enumerate(resources):
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            # Core: win contest on resources (higher if opponent farther)
            val = (od - sd) * 1000

            # Prefer getting closer soon, but don't ignore immediate pickup
            val += (max(0, 12 - sd) * 18)

            # Small penalty if opponent is already very close (reduce flip)
            if od <= 2:
                val -= (3 - od) * 30

            # Tie-breaker deterministically
            val += ((sd + rx + ry + i) % 3) * 2

            if sd < my_best:
                my_best = sd
            if val > score_move:
                score_move = val

        # Secondary: if scores tie, choose smaller distance to any resource
        key = (dx, dy)
        if (score_move > best[1]) or (score_move == best[1] and my_best < best[2]):
            best = (key, score_move, my_best)

    return [best[0][0], best[0][1]]