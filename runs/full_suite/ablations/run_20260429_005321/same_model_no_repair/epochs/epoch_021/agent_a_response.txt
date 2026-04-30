def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    def best_dist_from(x, y):
        if not resources:
            return 10**9
        bd = 10**9
        for rx, ry in resources:
            d = man(x, y, rx, ry)
            if d < bd:
                bd = d
        return bd

    # If no resources, move toward opponent while avoiding obstacles
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d_op = man(nx, ny, ox, oy)
            key = (d_op, abs(nx - ox) + abs(ny - oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best is not None else [0, 0]

    # Score moves by distance advantage to nearest resource after the move
    best_score = -10**18
    best_moves = []
    self_bd_now = best_dist_from(sx, sy)
    opp_bd_now = best_dist_from(ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        self_bd = best_dist_from(nx, ny)
        opp_bd = best_dist_from(ox, oy)

        # Advantage: how much closer we become than opponent compared to current state
        # Also reward lowering our own distance and penalize increasing opponent distance (if it changes via resource set it doesn't, so just keep closeness)
        advantage = (opp_bd - self_bd) - (opp_bd_now - self_bd_now)

        # Small tie-break: prefer moves that reduce our distance, then those closer to centerline between players
        move_pen = 0
        if dx == 0 and dy == 0:
            move_pen = 0.01  # prefer moving unless equally good

        center_bias = man(nx, ny, (w - 1) / 2, (h - 1) / 2) * 1e-6

        score = 1000 * advantage + 10 * (self_bd_now - self_bd) - move_pen - center_bias

        if score > best_score + 1e-12:
            best_score = score
            best_moves = [(dx, dy)]
        elif abs(score - best_score) <= 1e-12:
            best_moves.append((dx, dy))

    # Deterministic selection order among ties: lexicographic on (dx, dy)
    best_moves.sort(key=lambda t: (t[0], t[1]))
    return [best_moves[0][0], best_moves[0][1]] if best_moves else [0, 0]