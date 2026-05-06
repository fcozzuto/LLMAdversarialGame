def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None

    # Fallback target (roughly center) if no resources
    tx, ty = w // 2, h // 2

    # Deterministic preference ordering when scores tie
    tie_order = {m: i for i, m in enumerate(moves)}

    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if not valid(nx, ny):
            continue

        # Evaluate move by best advantage over all resources
        if resources:
            best_adv_score = None
            for r in resources:
                if not r or len(r) < 2:
                    continue
                rx, ry = int(r[0]), int(r[1])
                if not valid(rx, ry):
                    continue
                self_d = man(nx, ny, rx, ry)
                opp_d = man(ox, oy, rx, ry)
                # Prefer resources where we can be closer than opponent, but also keep self_d small
                # opp_d - self_d is "who's ahead"; scale it up a bit.
                adv = (opp_d - self_d)
                score = (2.0 * adv) - (0.4 * self_d)
                if best_adv_score is None or score > best_adv_score:
                    best_adv_score = score

            if best_adv_score is None:
                best_adv_score = -(0.8 * man(nx, ny, tx, ty))
        else:
            best_adv_score = -(0.8 * man(nx, ny, tx, ty))

        # Small safety: avoid moving too close to opponent unless it helps resource advantage
        dist_opp = man(nx, ny, ox, oy)
        safe_score = 0.05 * dist_opp

        total = best_adv_score + safe_score

        if best_score is None or total > best_score:
            best_score = total
            best_move = [dx, dy]
        elif total == best_score:
            # tie-break deterministically by move order
            if tie_order[(dx, dy)] < tie_order[(best_move[0], best_move[1])]:
                best_move = [dx, dy]

    return best_move