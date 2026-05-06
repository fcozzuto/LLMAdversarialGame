def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        if dx < 0: dx = -dx
        dy = by - ay
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    moves.sort()

    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [dx, dy]
        return [0, 0]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    # Deterministic target selection: maximize our advantage (opp_time - my_time).
    # Add small bias to central resources to counter edge patrol.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    resources_sorted = sorted(resources, key=lambda r: (-(cheb(sx, sy, r[0], r[1])), abs(r[0] - cx) + abs(r[1] - cy), r[0], r[1]))

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            nx, ny = sx, sy
        # If already on an obstacle (shouldn't happen), stay.
        if (nx, ny) in obs:
            continue

        val = 0
        # Evaluate best resource under this move.
        local_best = -10**18
        for rx, ry in resources_sorted:
            my_t = cheb(nx, ny, rx, ry)
            op_t = cheb(ox, oy, rx, ry)
            # Encourage capturing sooner: positive when we are closer than opponent.
            adv = op_t - my_t
            # Mild central preference; slight discouragement for moving away from center when tie.
            center_bias = -(abs(rx - cx) + abs(ry - cy)) * 0.01
            # Prefer near-term resources to reduce dithering.
            horizon = -(my_t) * 0.05
            score = adv + center_bias + horizon
            if score > local_best:
                local_best = score

        # Safety shaping: avoid moves that get immediately too close to obstacles.
        if obs:
            mind = 10
            for bx, by in obs:
                d = cheb(nx, ny, bx, by)
                if d < mind:
                    mind = d
            if mind <= 1:
                val = -10**9
            else:
                val = local_best - (1.0 / mind) * 0.1

        else:
            val = local_best

        # Deterministic tie-break: prefer staying only if equal, else prefer lexicographically smaller move.
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]