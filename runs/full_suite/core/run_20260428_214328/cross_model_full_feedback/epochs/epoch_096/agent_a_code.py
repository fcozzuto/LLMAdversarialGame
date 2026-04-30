def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    resources.sort()  # deterministic tie-breaking

    # Prefer moves that secure resources where we are closer than opponent; otherwise minimize loss.
    best_move = (0, 0)
    best_val = None
    opp_adj_risk = cheb((ox, oy), (sx, sy)) <= 1  # if we are too close, be cautious

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obst:
            continue

        self_pos = (nx, ny)
        opp_dist_to_self = cheb(self_pos, (ox, oy))

        val = 0
        # Strongly discourage stepping next to opponent if they are close
        if opp_adj_risk and opp_dist_to_self <= 1:
            val -= 20

        # Evaluate best resource by advantage
        local_best = None
        for rx, ry in resources:
            rpos = (rx, ry)
            sd = cheb(self_pos, rpos)
            od = cheb((ox, oy), rpos)
            adv = od - sd  # positive if we are closer
            # Reward advantage, slightly penalize being farther than necessary
            score = adv * 10 - sd
            if local_best is None or (score > local_best[0]) or (score == local_best[0] and (rx, ry) < local_best[1]):
                local_best = (score, (rx, ry))
        if local_best is None:
            # No resources visible: drift toward opponent's side corner (deterministic)
            target = (w - 1, h - 1)
            val += -cheb(self_pos, target)
        else:
            val += local_best[0]
            # If we are currently losing on all resources, reduce by total immediate risk
            if local_best[0] <= 0:
                val -= cheb(self_pos, (ox, oy))  # go away a bit

        # Tie-break: prefer not moving through (obvious) obstacle-adjacent positions? Minimal.
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]