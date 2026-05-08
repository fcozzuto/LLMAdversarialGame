def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # If there exists any resource we can reach not later than opponent, prioritize those (collect-first).
    # Otherwise, play denial: move to reduce opponent's lead.
    best_move = [0, 0]
    best_val = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        # score: combine collect-favoring and denial-favoring deterministically
        collect_candidates = 0
        val = 0
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive => we are closer after the move
            if lead >= 0:
                collect_candidates += 1
                # prefer nearer and larger lead; also slightly prefer cells closer to the resource
                val += (lead * 50) - ds
            else:
                # if we can't collect first, reduce the opponent lead (denial)
                val += lead * 10

        # obstacle avoidance / congestion: discourage stepping adjacent to obstacles
        # (keeps behavior different from the previous policy's target-only logic)
        adj_pen = 0
        for (ax, ay) in obs:
            if cheb(nx, ny, ax, ay) <= 1:
                adj_pen += 8
        val -= adj_pen

        # global bias: if any collectable resource exists, strongly prioritize those moves
        if collect_candidates > 0:
            val += 200

        # tie-break: prefer smaller move distance to nearest resource
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
        elif val == best_val:
            # deterministic tie-break using distance to closest resource after the move
            def min_d(cx, cy):
                md = 10**9
                for rx, ry in resources:
                    d = cheb(cx, cy, rx, ry)
                    if d < md:
                        md = d
                return md
            if min_d(nx, ny) < min_d(sx + best_move[0], sy + best_move[1]):
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]