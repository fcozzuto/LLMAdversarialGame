def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Deterministic tie-breaking order: sort by dx,dy so output is stable
    legal.sort(key=lambda t: (t[0], t[1]))

    best_dx, best_dy = 0, 0
    best_val = -10**18
    for dx, dy, nx, ny in legal:
        # Race-aware best target from next position
        best_r = -10**18
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            ds = manh(nx, ny, rx, ry)
            do = manh(ox, oy, rx, ry)
            # Prefer resources we can reach strictly earlier; penalize equal/behind
            # Also prefer closer targets overall to reduce chance of getting stuck.
            lead = do - ds  # positive if we are closer
            val = 200 * lead - 5 * ds
            # If opponent is very close, additional deterrence
            if do <= ds:
                val -= 120
            if val > best_r:
                best_r = val
        # Small bias to keep moving (avoid repeated staying) while respecting legality
        step_bias = -1 if (dx == 0 and dy == 0) else 0
        total = best_r + step_bias
        if total > best_val:
            best_val = total
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]