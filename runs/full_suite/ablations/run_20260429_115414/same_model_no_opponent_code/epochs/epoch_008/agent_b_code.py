def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0); best_val = None

    if resources:
        # Choose strategically: prefer moves that reduce our distance to a promising resource
        # and increase opponent distance to that same resource.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            val = 0.0
            # Evaluate against the single best "contested" resource for us after this move
            best_cont = None
            for rx, ry in resources:
                d_self = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                # Contention margin: positive means we are closer than opponent
                margin = d_opp - d_self
                # Prefer small distance strongly; use margin to contest
                cont = (d_self, -margin, rx, ry)
                if best_cont is None or cont < best_cont:
                    best_cont = cont
            # best_cont: (d_self, -margin, rx, ry)
            d_self, neg_margin, rx, ry = best_cont
            margin = -neg_margin
            # Larger margin better; tie-breaker by resource coordinates deterministically
            val = (1000 - d_self * 10) + margin * 3 - (rx * 0.01 + ry * 0.001)

            if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: drift toward center while avoiding letting opponent get closer to us
    cx, cy = (w - 1) // 2, (h - 1) // 2
    # Prefer increasing our distance from opponent slightly while approaching center
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_center = cheb(nx, ny, cx, cy)
        d_opp = cheb(nx, ny, ox, oy)
        d_opp_now = cheb(sx, sy, ox, oy)
        val = (-d_center * 2.0) + (d_opp - d_opp_now) * 3.0
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]