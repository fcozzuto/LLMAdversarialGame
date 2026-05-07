def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    env = observation.get("environment_name", "")
    my = (sx, sy)
    opp = (ox, oy)

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Targeting: counter "sweep_rows" by prioritizing resources aligned with opponent's row (or near it),
    # while still favoring resources where we can arrive no later than opponent.
    best_r = None
    best_val = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry):
            continue
        if (rx, ry) in obstacles:
            continue
        md = cheb(my, (rx, ry))
        od = cheb(opp, (rx, ry))
        row_bias = abs(ry - oy)  # opponent sweeping rows: contest near its current row
        # We want smaller md and larger gap (od - md). Penalize if opponent is much faster.
        val = md + 0.75 * row_bias + (0.9 * max(0, md - od)) + (-1.1 * max(0, od - md))
        if best_val is None or val < best_val:
            best_val = val
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]

    tx, ty = best_r

    # Move selection with obstacle avoidance and slight anti-opponent pressure
    def step_score(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return 10**9
        nm = (nx, ny)
        md = cheb(nm, (tx, ty))
        # Prefer moves that reduce our arrival time and (secondarily) avoid giving opponent an easy line.
        od = cheb(opp, (tx, ty))
        opp_row = abs(ty - oy)
        return md - 0.25 * max(0, od - md) + 0.1 * opp_row

    best_step = None
    best_s = None
    for dx, dy in moves:
        s = step_score(dx, dy)
        if best_s is None or s < best_s:
            best_s = s
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]