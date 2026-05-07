def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    # For each move, choose the resource we would then "secure" best (lead over opponent).
    best_move = None
    best_val = None
    for dx, dy, nx, ny in legal:
        # Immediate gain: if we step onto a resource, strongly prefer.
        immediate = 0
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if rx == nx and ry == ny:
                immediate = 10_000
                break

        # Pick the most favorable resource for us after this move.
        best_lead = None
        best_selfd = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            lead = opp_d - self_d  # positive means we are closer (in max-step metric)
            # Tie-break: prefer smaller self_d, then larger opp_d.
            key = (lead, -self_d, opp_d)
            if best_lead is None or key > best_lead:
                best_lead = key
                best_selfd = self_d

        val = (immediate + best_lead[0], best_lead[1], best_lead[2])
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]