def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

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

    # Deterministic bias: prefer moves that advance along x/y balance to reduce oscillation
    bias = (sx + sy + observation.get("turn_index", 0)) % 2

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy

        # Score this move by the best resource we could aim to collect next.
        move_val = -10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Huge reward for being strictly closer; penalty if opponent is closer.
            # Also include direct distance pressure and small deterministic tie-break.
            val = (od - sd) * 1000 - sd
            val += ((sd + rx + ry + bias) % 3) * 2
            # If we can step onto the resource immediately, dominate.
            if sd == 0:
                val += 10**6
            if val > move_val:
                move_val = val

        if move_val > best_val:
            best_val = move_val
            best_move = [dx, dy]

    return best_move