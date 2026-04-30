def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    oppd = cheb(sx, sy, ox, oy)
    prefer = []  # (advantage, dist, x, y) for resources where we can be closer
    for x, y in resources:
        d_ = cheb(sx, sy, x, y)
        d_o = cheb(ox, oy, x, y)
        adv = d_o - d_
        prefer.append((adv, d_, x, y))

    # Choose best move by maximizing "advantage-first" toward a contested/available resource, avoid proximity to opponent
    best_move = (0, 0)
    best_score = -10**18
    # Use a fixed iteration order; deterministic tie-break by move order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Evaluate target choice for this move
        best_local = -10**18
        hit_enemy = 0
        nd_opp = cheb(nx, ny, ox, oy)
        if nd_opp <= 1:
            hit_enemy = 1

        if resources:
            # Favor resources where we are (or become) closer than opponent; otherwise still go for best advantage gain
            for adv0, d0, x, y in prefer:
                nd_ = cheb(nx, ny, x, y)
                nd_o = cheb(ox, oy, x, y)
                adv = nd_o - nd_
                # score: strongly prefer increasing our advantage; also move toward the resource
                # Add slight bonus for increasing separation from opponent.
                score = 20 * adv - nd_ + 0.05 * nd_o - (12 if hit_enemy else 0)
                if adv < 0:
                    score -= 8  # discourage losing contests
                # Extra: prefer moves that reduce minimum distance to any resource
                if adv >= 0:
                    score += 2
                if score > best_local:
                    best_local = score
        else:
            tx, ty = w // 2, h // 2
            best_local = -cheb(nx, ny, tx, ty) + 0.05 * cheb(nx, ny, ox, oy) - (12 if hit_enemy else 0)

        # If opponent is very close, add more separation weight
        if oppd <= 2:
            best_local += (nd_opp - 1)

        if best_local > best_score:
            best_score = best_local
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]