def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def manh_or_cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy  # Chebyshev on 8-neighbor

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    if not ok(sx, sy):
        return [0, 0]

    # Score each move by best resource advantage after the move; advantage favors states where we're closer than opponent.
    best_val = -10**18
    best_move = [0, 0]

    # Deterministic preference ordering: same value -> earlier in dirs list
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy  # engine would keep us, treat as such deterministically
            dx, dy = 0, 0

        if resources:
            # Evaluate by choosing the single best target for us, then maximizing (opp_dist - our_dist) and our closeness.
            # Also include slight term to prefer taking resources on same "front" toward opponent.
            worst = -10**18
            for rx, ry in resources:
                od = manh_or_cheb(ox, oy, rx, ry)
                nd = manh_or_cheb(nx, ny, rx, ry)
                adv = od - nd  # positive means we are closer/equal
                # Encourage pushing toward opponent side and reducing distance to opponent
                push = (rx - nx) * (ox - sx) + (ry - ny) * (oy - sy)
                push = push if push > 0 else 0
                val = adv * 1000 - nd * 10 + push
                if val > worst:
                    worst = val
            val = worst
        else:
            # No visible resources: move to center then toward opponent side deterministically.
            cx, cy = w // 2, h // 2
            val = -manh_or_cheb(nx, ny, cx, cy) + (manh_or_cheb(nx, ny, ox, oy) * -0.1)

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    # If all move evaluations collapse (shouldn't), keep still deterministically
    return [int(best_move[0]), int(best_move[1])]