def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Target direction: choose resource giving maximum advantage (deterministic tie-break).
    tx, ty = sx, sy
    if resources:
        best_r = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            key = (-adv, myd, rx, ry)  # minimal key => max advantage, then closer, then lexicographic
            if best_r is None or key < best_r[0]:
                best_r = (key, (rx, ry), adv)
        tx, ty = best_r[1]
    else:
        tx, ty = (W - 1) // 2, (H - 1) // 2

    # Evaluate local candidate moves
    center_x, center_y = (W - 1) / 2.0, (H - 1) / 2.0
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if resources:
            # Compute best advantage reachable for any resource from this candidate
            max_adv = -10**9
            min_my = 10**9
            min_opp = 10**9
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                adv = opd - myd
                if adv > max_adv:
                    max_adv = adv
                if myd < min_my:
                    min_my = myd
                if opd < min_opp:
                    min_opp = opd
            # Encourage securing an advantage and not drifting too far
            val = max_adv * 10 + (min_opp - min_my) - cheb(nx, ny, tx, ty) * 0.1
            # Small tie-break favor moving toward center a bit (deterministic)
            val -= abs(nx - center_x) * 0.01 + abs(ny - center_y) * 0.01
        else:
            # No resources known: head to center / keep safe
            val = -cheb(nx, ny, tx, ty)

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]