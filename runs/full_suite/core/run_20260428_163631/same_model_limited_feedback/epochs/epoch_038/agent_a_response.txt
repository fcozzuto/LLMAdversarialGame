def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx
        dy = ay - by
        return (dx*dx + dy*dy) ** 0.5

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    best = None
    best_val = -1e18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # If we are already on a resource, just stay to secure it.
        if (nx, ny) in set(tuple(r) for r in resources):
            return [dx, dy]
        my = (nx, ny)
        opp = (ox, oy)

        # Materially different tactic: choose a target where we gain over opponent;
        # otherwise prioritize nearest resource to keep tempo.
        if resources:
            target_score = -1e18
            for rx, ry in resources:
                r = (rx, ry)
                md = dist(my, r)
                od = dist(opp, r)
                gain = od - md  # positive means we are closer
                # Encourage grabbing resources quickly; strongly prefer advantage.
                val = (gain * 5.0) - md * 1.0
                # Mildly discourage targets near obstacles by penalizing if our move would likely hit obstacles next step.
                if md > 0:
                    # look at one-step adjacency risk
                    step_block = 0
                    for ddx, ddy in moves:
                        tx, ty = int(nx + ddx), int(ny + ddy)
                        if (0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles):
                            step_block += 1
                    val -= step_block * 0.05
                if val > target_score:
                    target_score = val
            # If no advantage available, still choose best tempo.
            val_total = target_score
        else:
            val_total = -dist(my, opp)

        # Extra obstacle-aware tiebreak: avoid staying if it doesn't help.
        if best is None or val_total > best_val + 1e-9:
            best_val = val_total
            best = (dx, dy)
    return [int(best[0]), int(best[1])]