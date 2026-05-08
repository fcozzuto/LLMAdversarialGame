def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if role == "evader":
        # Evader: head to a corner farthest from pursuer to reduce direct capture pressure.
        tx, ty = max(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))
        want_increase = True
    else:
        # Pursuer: aim for nearest corner for a deterministic drift that often compresses paths.
        tx, ty = min(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))
        want_increase = False

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocked:
            continue

        dcur2 = (sx - ox) * (sx - ox) + (sy - oy) * (sy - oy)
        dnext2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        dd = dnext2 - dcur2

        # Progress toward chosen corner (tie-breaker).
        prog_cur = abs(tx - sx) + abs(ty - sy)
        prog_next = abs(tx - nx) + abs(ty - ny)
        prog = prog_next - prog_cur  # negative is good

        # If role is evader, prefer increasing distance; if pursuer, prefer decreasing distance.
        dist_term = dd if want_increase else -dd

        # Strongly prefer any move that reduces distance to opponent for pursuer,
        # or increases it for evader.
        if role == "pursuer" and dnext2 == 0:
            return [dx, dy]
        if role == "evader" and dnext2 > dcur2:
            bonus = 1
        else:
            bonus = 0

        # Deterministic scoring: maximize primary, then progress, then prefer staying/more "forward".
        score = (dist_term, -abs(prog), bonus, -(abs(tx - nx) + abs(ty - ny)), -abs(dx) - abs(dy))
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [0, 0] if best is None else [int(best[0]), int(best[1])]