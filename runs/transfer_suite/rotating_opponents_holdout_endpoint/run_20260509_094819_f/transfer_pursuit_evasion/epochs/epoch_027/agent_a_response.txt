def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or ("escape" in role) or ("escape" in (observation.get("environment_name", "") or "").lower())
    is_pursuer = not is_evader

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    best = None
    best_score = None

    # Deterministic tie-break: score then order in moves list
    for idx, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_now = cheb(sx, sy, ox, oy)
        d_new = cheb(nx, ny, ox, oy)

        # Predict opponent mobility after our move only via static obstacles (lightweight)
        omob = mobility(ox, oy)

        # Evader: maximize distance and keep opponent from getting good angles by staying in low-opponent-mobility zones (relative).
        # Pursuer: minimize distance and move into places that increase our capture pressure by reducing our next-step mobility gaps.
        if is_pursuer:
            # Prefer closing in; also prefer lowering opponent mobility (harder for them to escape).
            score = (-d_new * 10.0) + ((omob - mobility(nx, ny)) * 0.5) + (1.0 if d_new < d_now else 0.0)
            # Slightly prefer moving toward center to avoid being corner-trapped by zigzags
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score += -0.01 * (abs(nx - cx) + abs(ny - cy))
        else:
            # Evader: keep away; prefer moves that reduce our vulnerability by maintaining higher mobility.
            score = (d_new * 10.0) + (mobility(nx, ny) * 1.0) + (-omob * 0.1)
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score += 0.01 * (abs(nx - cx) + abs(ny - cy))

        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]