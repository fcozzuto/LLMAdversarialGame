def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    best = None
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        # Prefer resources where we are (or become) much closer than opponent.
        target_bonus = -10**18
        for r in resources:
            d_my = dist((nx, ny), r)
            d_op = dist((ox, oy), r)
            # If opponent is closer, strongly reduce; otherwise reward by the gap.
            gap = d_op - d_my
            val = gap * 20 - d_my
            if val > target_bonus:
                target_bonus = val

        # Add light anti-collision / contest control: avoid stepping toward opponent if tied.
        d_op_now = dist((sx, sy), (ox, oy))
        d_op_new = dist((nx, ny), (ox, oy))
        opp_penalty = (d_op_new - d_op_now) * 2  # discourage approaching when not winning a target
        step_cost = (abs(dx) + abs(dy)) * 0.5
        score = target_bonus - opp_penalty - step_cost

        # Deterministic tie-break: lexicographic by dx,dy order above.
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best