def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    my = (sx, sy)
    opp = (ox, oy)

    if not resources:
        tx = (w // 2) if sx < w // 2 else (w // 2 - 1 if sx > w // 2 - 1 else sx)
        ty = (h // 2) if sy < h // 2 else (h // 2 - 1 if sy > h // 2 - 1 else sy)
        target = (tx, ty)
    else:
        best = None
        best_score = -10**18
        for r in resources:
            myd = cheb(my, r)
            opd = cheb(opp, r)
            # Prefer resources where we have a reach advantage; tie-break by closer distance.
            advantage = opd - myd
            score = advantage * 10 - myd
            # If we are equally far or behind, still choose nearer ones but slightly penalize.
            if advantage < 0:
                score -= (-advantage) * 3
            if best is None or score > best_score:
                best_score = score
                best = r
        target = best

    # Evaluate next move with simple deterministic "contest" and obstacle-safe preference.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nxt = (nx, ny)
        d_my = cheb(nxt, target)
        d_opp = cheb(opp, target)

        # Strongly prioritize reducing our distance to target.
        val = -d_my * 100

        # If opponent is also near target, avoid moves that increase relative disadvantage.
        rel = d_opp - d_my
        val += rel * 25

        # Local safety: discourage moving adjacent to opponent (competition blocking).
        oppd = cheb(nxt, opp)
        if oppd <= 1:
            val -= (2 - oppd) * 80

        # Mild preference for advancing overall (avoid oscillation by preferring diagonals toward goal when tied).
        if (dx != 0 and dy != 0) and (cheb(my, target) == cheb(nxt, target)):
            val += 1

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]