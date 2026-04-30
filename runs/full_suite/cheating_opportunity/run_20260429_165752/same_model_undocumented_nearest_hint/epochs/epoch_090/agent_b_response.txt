def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    if not resources:
        # Fall back to moving toward the center while keeping away from obstacles.
        tx, ty = (W - 1) // 2, (H - 1) // 2
    else:
        center_x, center_y = (W - 1) / 2.0, (H - 1) / 2.0
        dx_between = (ox - sx)
        dy_between = (oy - sy)

        best = None
        best_score = -10**18
        for rx, ry in resources:
            dS = cheb(sx, sy, rx, ry)
            dO = cheb(ox, oy, rx, ry)
            # Key change: strong preference for resources where we are significantly closer than opponent.
            close_adv = dO - dS  # larger is better
            # Tie-break: prefer resources more "toward our side" and toward center line region.
            side = (rx - (W - 1 - rx)) * (1 if dx_between >= 0 else -1) + (ry - (H - 1 - ry)) * (1 if dy_between >= 0 else -1)
            center_bonus = -(abs(rx - center_x) + abs(ry - center_y))
            # Mild penalty if opponent is extremely close (to avoid getting contested where we can't secure quickly).
            contest_pen = 0
            if dO <= 2 and dS >= dO:
                contest_pen = 6
            score = 20 * close_adv - 2 * dS + 0.2 * side + 0.1 * center_bonus - contest_pen
            if score > best_score:
                best_score = score
                best = (rx, ry)
        tx, ty = best

    # Greedy step toward target, with deterministic obstacle-aware tie-breaking.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Prefer smaller distance to target; also prefer increasing distance from opponent.
        val = -3 * d_to + 0.2 * d_opp
        # Deterministic tie-break: lexicographic on (dx,dy) with a fixed ordering.
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]