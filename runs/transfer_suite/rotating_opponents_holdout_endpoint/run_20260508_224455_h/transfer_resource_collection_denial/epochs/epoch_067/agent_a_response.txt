def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    gw, gh = int(observation["grid_width"]), int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy

    # Opponent sweep_rows bias: prefer resources on rows that are "behind" opponent relative to us.
    # If opponent is above us (oy < sy), prefer smaller y; if below, prefer larger y.
    row_pref = -1 if oy < sy else (1 if oy > sy else 0)

    def best_target(px, py):
        best = None  # (score, self_d, opp_d, rx, ry)
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            sd = cheb(px, py, rx, ry)
            od = cheb(ox, oy, rx, ry)
            advantage = od - sd  # larger is better (we reach earlier)
            # Penalize aiming at opponent-favorable rows (where sweep_rows likely moves)
            row_bias = row_pref * (ry - sy)  # if row_pref=-1, smaller ry favored; if +1, larger favored
            # Keep it subtle/deterministic:
            score = advantage * 100 + (-row_bias)  # higher better
            key = (score, -sd, -od, rx, ry)
            if best is None or key > best[0]:
                best = (key, sd, od, (rx, ry))
        return best[3]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # One-step lookahead: choose move that maximizes advantage to the best target from the next position,
    # while avoiding obstacles by construction and slightly preferring safer moves away from obstacles.
    def obstacle_proximity_cost(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        rx, ry = best_target(nx, ny)
        sd = cheb(nx, ny, rx, ry)
        od = cheb(ox, oy, rx, ry)
        val = (od - sd) * 1000 - sd * 3 - obstacle_proximity_cost(nx, ny) * 5
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move