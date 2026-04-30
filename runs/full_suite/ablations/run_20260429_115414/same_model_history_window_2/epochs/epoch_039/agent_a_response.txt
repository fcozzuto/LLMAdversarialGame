def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    # Bias: early game expand toward nearest resource frontier; late game slightly prioritize racing opponent.
    remaining = int(observation.get("remaining_resource_count") or len(resources) or 0)
    turn = int(observation.get("turn_index") or 0)
    late = 1 if (remaining <= 4 or turn >= 40) else 0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if resources:
            d_self = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            # Predict contention: reduce value if opponent is closer to the same nearest resource region.
            d_opp = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
            # Also estimate "advantage" on nearest target by comparing closest distances from next vs current.
            d_self_now = min(cheb(sx, sy, rx, ry) for rx, ry in resources)
            self_improve = d_self_now - d_self
            # Tie-break: move that increases distance from opponent when not racing.
            opp_dist = cheb(nx, ny, ox, oy)
            my_goal = -d_self
            race = (d_opp - d_self) if late else (d_self_now - d_opp)
            val = my_goal * 10 + self_improve * 3 + race * 4 + opp_dist * (1 if not late else -0.5)
        else:
            # If no resources visible, go to center to avoid edge traps.
            cx, cy = (w - 1) // 2, (h - 1) // 2
            val = -cheb(nx, ny, cx, cy) - cheb(nx, ny, ox, oy) * 0.1
        # Deterministic tie-break: prefer smaller dx, then smaller dy in move list order.
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]