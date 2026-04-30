def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        # Move toward center while avoiding obstacles
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if (nx, ny) in blocked or not inb(nx, ny):
                continue
            v = -cheb(nx, ny, cx, cy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Target selection: prioritize resources where we have a "tempo" advantage
    best_score = -10**30
    best_move = (0, 0)
    cx, cy = (w - 1) // 2, (h - 1) // 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        # Immediate danger: stepping closer to opponent if we lose tempo
        center_pref = -cheb(nx, ny, cx, cy)
        tempo_sum = 0
        take_bonus = 0

        for rx, ry in resources:
            if (rx, ry) in blocked:
                continue
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)

            # We want opp_d - our_d large (we are closer).
            adv = opp_d - our_d

            # If we could be the next collector for a nearby resource, add bonus.
            # (Exact collection mechanics unknown; use heuristic based on being very close.)
            if our_d == 0:
                take_bonus += 20000
            elif our_d == 1 and adv >= 0:
                take_bonus += 4000
            elif our_d <= 2 and adv >= 1:
                take_bonus += 800

            # Also penalize resources where opponent is much closer.
            tempo_sum += adv * 120 - our_d * 3

        # Additional opponent-response: if many resources give negative adv, reduce staying.
        opp_prox = cheb(nx, ny, ox, oy)
        opp_pen = opp_prox * 1

        val = tempo_sum + take_bonus + center_pref * 2 - opp_pen
        # Deterministic tie-break by preferring smaller steps (closer to standing still) then coords
        if val > best_score or (val == best_score and (dx*dx + dy*dy, nx, ny) < (best_move[0]*best_move[0] + best_move[1]*best_move[1], sx + best_move[0], sy + best_move[1])):
            best_score = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]