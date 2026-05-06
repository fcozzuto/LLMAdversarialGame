def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)
    def che(ax, ay, bx, by): return max(abs(ax - bx), abs(ay - by))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move, best_val = (0, 0), None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Choose a target resource that we can improve on now vs the opponent.
        my_best = 10**9
        opp_best = 10**9
        for tx, ty in resources:
            myd = man(nx, ny, tx, ty)
            opd = man(ox, oy, tx, ty)
            if myd < my_best:
                my_best = myd
            if opd < opp_best:
                opp_best = opd

        # Advantage: want to get closer than opponent to the same nearby resources.
        # Also prefer moves that reduce opponent's closest-resource distance.
        # Tie-break: prefer moving towards the center.
        center_bias = -(abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
        val = (opp_best - my_best) * 50 - my_best * 3 + center_bias

        # Small safety: avoid getting too close to opponent if we can't also be closer to resources.
        opp_dist = che(nx, ny, ox, oy)
        if opp_dist <= 1:
            val -= 10

        if best_val is None or val > best_val:
            best_val, best_move = val, (dx, dy)
        elif val == best_val:
            # Deterministic tie-break: smaller manhattan delta, then lexicographic dx,dy
            if abs(dx) + abs(dy) < abs(best_move[0]) + abs(best_move[1]) or (abs(dx) + abs(dy) == abs(best_move[0]) + abs(best_move[1]) and (dx, dy) < best_move):
                best_move = (dx, dy)

    # If all candidate moves were invalid (should be rare), stay.
    return [int(best_move[0]), int(best_move[1])]