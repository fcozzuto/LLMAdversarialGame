def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    occ = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev: diagonal = 1 per step

    if not resources:
        return [0, 0]

    # Pick a resource we can arrive at earlier (race), else the one that minimizes our "behindness"
    best_r = resources[0]
    best_key = None
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        lead = od - sd  # positive => we are ahead
        # Prefer being ahead strongly; then be fast; then prefer central-ish deterministic tiebreak
        key = (-(lead > 0), -lead, sd, abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)
    rx, ry = best_r

    # Candidate move: go to cell that reduces our distance to target while improving lead
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # If we try to step into obstacle, it effectively stays; penalize it heavily
        if (nx, ny) in occ:
            val = (10**9, 10**9, 10**9, dx*dx + dy*dy)
        else:
            sd2 = dist(nx, ny, rx, ry)
            od2 = dist(ox, oy, rx, ry)
            lead2 = od2 - sd2
            # Mildly avoid getting adjacent to obstacles to reduce risk of being trapped by sweep behavior
            adj_obs = 0
            if obstacles:
                for ax, ay in obstacles:
                    if max(abs(ax - nx), abs(ay - ny)) == 1:
                        adj_obs += 1
            val = (-(lead2 > 0), -lead2, sd2, adj_obs, dx*dx + dy*dy)
        if best_val is None or val < best_val:
            best_val = val
            best = [dx, dy]

    return best