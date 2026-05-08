def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role_s = str(observation.get("self_role", "")).lower()
    is_evader = any(k in role_s for k in ("evader", "runner", "flee", "fleeing", "evade", "avoid"))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        return dx if dx > dy else dy

    def mobility(x, y):
        m = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                m += 1
        return m

    # One-step lookahead: avoid/seek positions where opponent can immediately capture.
    # With capture_radius=0, capture occurs if distance becomes 0.
    best = None
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        dist_now = cheb(nx, ny, ox, oy)
        imm_capture = (dist_now == 0)

        # Opponent response distance after their best next move (only uses geometry).
        # If we are pursuer, assume opponent is evader; if we are evader, assume opponent pursues.
        # This is a heuristic but deterministic and cheap.
        opp_dist_best = None
        for odx, ody in deltas:
            tx, ty = ox + odx, oy + ody
            if not inb(tx, ty) or (tx, ty) in blocked:
                continue
            d = cheb(nx, ny, tx, ty)
            if opp_dist_best is None:
                opp_dist_best = d
            else:
                # If opponent is pursuing, they minimize our distance; else they maximize.
                if is_evader:
                    # opponent is pursuer => minimize distance to us
                    if d < opp_dist_best:
                        opp_dist_best = d
                else:
                    # opponent is evader => maximize distance from us
                    if d > opp_dist_best:
                        opp_dist_best = d

        # Scoring: higher is better for our final objective.
        mob = mobility(nx, ny)
        if is_evader:
            # Want to survive: maximize distance; strongly avoid immediate capture.
            val = (0 if imm_capture else 100000) + opp_dist_best * 10 + mob
        else:
            # Want to capture: minimize distance; strongly avoid being separated too much.
            val = (0 if imm_capture else -100000) - dist_now * 10 + mob

        # Deterministic tie-break: prefer higher val, then higher mobility, then lexicographic move.
        key = (val, mob, dx, dy)
        if best is None:
            best, best_val = key, [dx, dy]
        else:
            if key > best:
                best, best_val = key, [dx, dy]

    # If no valid move (shouldn't happen), stay.
    if best_val is None:
        return [0, 0]
    return best_val