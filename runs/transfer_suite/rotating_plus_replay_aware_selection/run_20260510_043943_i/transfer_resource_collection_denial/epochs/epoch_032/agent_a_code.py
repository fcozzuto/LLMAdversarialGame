def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_raw)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def best_value_for_pos(x, y):
        if not resources:
            return -(man(x, y, ox, oy))
        best = -10**18
        for rx, ry in resources:
            ds = man(x, y, rx, ry)
            do = man(ox, oy, rx, ry)
            # Strongly favor resources where we have the time advantage; tie-break by closeness.
            adv = (do - ds) * 1000 - ds
            # Slightly prefer resources more distant from opponent (reduces their contest chance).
            adv -= (do) // 2
            if adv > best:
                best = adv
        return best

    best_val = -10**18
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        val = best_value_for_pos(nx, ny)
        # If equal, keep deterministic earliest move (deltas order).
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move