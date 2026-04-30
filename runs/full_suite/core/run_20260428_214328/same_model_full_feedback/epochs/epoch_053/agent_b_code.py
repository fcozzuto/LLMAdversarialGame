def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx if dx >= 0 else -dx if dy >= 0 else -dy

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if inside(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    # If no resources, drift toward center while pushing away from opponent.
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_m = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = (abs(nx - cx) + abs(ny - cy)) + 0.2 * cheb(nx, ny, ox, oy)
            if best is None or v < best:
                best, best_m = v, (dx, dy)
        return [best_m[0], best_m[1]]

    # Resource bidding: prefer resources I'm close to, and avoid ones the opponent is significantly closer to.
    best_val = None
    best_move = (0, 0)
    opp_close = 0
    for dx, dy in ((-1, -1), (1, 1), (-1, 1), (1, -1)):
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and cheb(nx, ny, ox, oy) <= 1:
            opp_close = 1
            break

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        my_step = 1  # movement cost proxy
        val = 0.0
        # Small bias to not step into immediate opponent vicinity; still allow if it gets resources.
        val += 0.15 * (cheb(nx, ny, ox, oy) == 0)
        val += 0.08 * (cheb(nx, ny, ox, oy) == 1) * (1 + 0.5 * opp_close)

        # Evaluate best target from this move
        best_target = None
        for tx, ty in resources:
            md = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # If opponent is closer, add a penalty; if my move makes me closer than opponent, reward.
            rel = od - md
            target_score = md + (0.9 if rel < 0 else -0.25) * (1 + (-rel if rel < 0 else 0))
            # Also bias toward resources closer to me in absolute terms
            target_score += 0.01 * (tx + ty)
            if best_target is None or target_score < best_target:
                best_target = target_score
        val += best_target
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]