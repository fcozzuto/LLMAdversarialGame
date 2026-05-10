def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for c in observation.get("obstacles", []) or []:
        x, y = c
        obstacles.add((int(x), int(y)))

    self_cells = set()
    for c in observation.get("self_territory", []) or []:
        x, y = c
        self_cells.add((int(x), int(y)))

    opp_cells = set()
    for c in observation.get("opponent_territory", []) or []:
        x, y = c
        opp_cells.add((int(x), int(y)))

    unclaimed = set()
    for c in observation.get("unclaimed_cells", []) or []:
        x, y = c
        unclaimed.add((int(x), int(y)))

    resources = []
    for r in observation.get("resources", []) or []:
        x, y = r
        resources.append((int(x), int(y)))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    opp = (ox, oy)
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)

        # Prefer flipping/claiming: opponent-owned or unclaimed.
        base = 0
        if cell in opp_cells:
            base += 3.2
        elif cell in unclaimed:
            base += 2.2
        elif cell in self_cells:
            base += 0.2
        else:
            base += 1.0  # safety for any missed cells

        # Contest: prefer cells we reach sooner than opponent.
        d_us = man((nx, ny), (sx, sy))
        d_opp = man(cell, opp)
        contest = -0.15 * d_opp

        # Keep some pressure away from dying corners: move toward center.
        center = -0.02 * (abs(nx - cx) + abs(ny - cy))

        # If resources exist, head toward nearest resource but only when it doesn't help opponent too much.
        res_term = 0.0
        if resources:
            mind = 10**9
            for rx, ry in resources:
                d = abs(nx - rx) + abs(ny - ry)
                if d < mind:
                    mind = d
            res_term = -0.05 * mind

        val = base + contest + center + res_term - 0.01 * d_us

        # Deterministic tiebreak: lexicographic by move order and then lower dx,dy magnitude.
        if val > best_val + 1e-12 or (abs(val - best_val) <= 1e-12 and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]