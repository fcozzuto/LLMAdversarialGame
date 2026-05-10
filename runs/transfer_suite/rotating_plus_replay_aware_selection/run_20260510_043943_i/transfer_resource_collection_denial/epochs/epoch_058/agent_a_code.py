def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    # Precompute opponent distance to each resource for deterministic comparisons
    rinfo = []
    for i, (rx, ry) in enumerate(resources):
        rinfo.append((rx, ry, man(ox, oy, rx, ry), (rx + ry + i) % 2))

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Look for the best "swing" resource given this move: we want (we earlier than opp) and closer overall
        cur_best = -10**18
        for rx, ry, od, parity in rinfo:
            sd = man(nx, ny, rx, ry)
            # If we're closer than opponent, huge reward; if not, penalize strongly (still allow if very close)
            lead = od - sd
            val = lead * 2000 - sd
            # Encourage committing to nearer resources and discourage moving toward opponent-favored ones
            val += (parity * 5) - (sd > 0) * 2
            if val > cur_best:
                cur_best = val

        # Small preference: reduce distance to the nearest resource to prevent dithering
        nearest = 10**9
        for rx, ry, _, _ in rinfo:
            sd0 = man(nx, ny, rx, ry)
            if sd0 < nearest:
                nearest = sd0
        cur_best += -nearest * 1

        # Deterministic tie-breaker based on move and current position
        tie = ((sx + sy + nx + ny) % 3) * 0.01 + (dx * 0.001 + dy * 0.0001)
        cur_best += tie

        if cur_best > best_val:
            best_val = cur_best
            best_move = [nx - sx, ny - sy]

    if best_move[0] not in (-1, 0, 1) or best_move[1] not in (-1, 0, 1):
        return [0, 0]
    return best_move