def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        dx = 0
        if sx < w - 1:
            dx = 1
        elif sx > 0:
            dx = -1
        dy = 0
        if sy < h - 1:
            dy = 1
        elif sy > 0:
            dy = -1
        return [dx, dy]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def cell_best_value(x, y):
        # Value aims to be the one where we are closer than opponent, and closer in absolute time.
        best = -10**18
        for rx, ry in resources:
            ds = abs(rx - x) + abs(ry - y)
            do = abs(rx - ox) + abs(ry - oy)
            # If we are closer (or tie), strongly prefer that resource.
            adv = do - ds
            # Encourage taking nearer resources even if not yet winning.
            time = -ds
            # Mild center preference to route away from corners.
            center = - (abs((w - 1) * 0.5 - x) + abs((h - 1) * 0.5 - y)) * 0.05
            # Small edge penalty
            edge_pen = -0.15 if (rx in (0, w - 1) or ry in (0, h - 1)) else 0.0
            val = adv * 12.0 + time * 2.0 + center + edge_pen
            if val > best:
                best = val
        return best

    best_move = [0, 0]
    best_score = -10**18
    # Deterministic tie-break: prefer smaller dx, then smaller dy, then earlier in move list.
    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sc = cell_best_value(nx, ny)

        # Add a local obstacle-avoidance / routing nudge: don't wander away from all resources.
        if resources:
            min_ds = min(abs(rx - nx) + abs(ry - ny) for rx, ry in resources)
            sc += -min_ds * 0.03

        # If this move would make us strictly worse than the opponent for the "most contested" resource, penalize slightly.
        # (Approximate by comparing current best and next-closest advantage)
        if resources:
            best_adv_now = max((abs(rx - ox) + abs(ry - oy)) - (abs(rx - sx) + abs(ry - sy)) for rx, ry in resources)
            best_adv_next = max((abs(rx - ox) + abs(ry - oy)) - (abs(rx - nx) + abs(ry - ny)) for rx, ry in resources)
            sc += (best_adv_next - best_adv_now) * 0.6

        if sc > best_score:
            best_score = sc
            best_move = [dx, dy]
        elif sc == best_score:
            if dx < best_move[0] or (dx == best_move[0] and dy < best_move[1]):
                best_move = [dx, dy]
            elif dx == best_move[0] and dy == best_move[1]:
                if i < moves.index((best_move[0], best_move[1])):
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]