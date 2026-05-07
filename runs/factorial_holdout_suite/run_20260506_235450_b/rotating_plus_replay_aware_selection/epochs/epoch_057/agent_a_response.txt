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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best_move = None
    best_val = None
    for dx, dy, nx, ny in moves:
        # Evaluate move by best contest outcome over all remaining resources.
        best_for_move = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            margin = opp_d - self_d  # higher means we are faster
            # If we lose a race, still go for closer-but-reasonable targets.
            val = margin * 1000 - self_d
            # Small tie-break: prefer resources more "toward center" to avoid getting stuck near corners.
            cx, cy = 3.5, 3.5
            val -= 0.5 * (abs(rx - cx) + abs(ry - cy))
            if best_for_move is None or val > best_for_move:
                best_for_move = val
        # If we can win any race from the moved position, prioritize it hard; else go for best win-likelihood.
        # Also slightly prefer moves that approach the closest resource.
        mind = min(cheb(nx, ny, int(r[0]), int(r[1])) for r in resources)
        win_bonus = max((cheb(ox, oy, int(r[0]), int(r[1])) - cheb(nx, ny, int(r[0]), int(r[1])) for r in resources), default=-999)
        total = best_for_move + win_bonus * 20 - mind
        if best_val is None or total > best_val:
            best_val = total
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]