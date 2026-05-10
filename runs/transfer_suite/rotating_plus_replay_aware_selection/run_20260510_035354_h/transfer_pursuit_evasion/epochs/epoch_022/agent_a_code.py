def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs_list = observation.get("obstacles", []) or []
    obs = set((int(p[0]), int(p[1])) for p in obs_list)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def obstacle_near(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if (nx, ny) in obs:
                    c += 1
        return c

    def legal_moves_count(x, y):
        cnt = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny):
                cnt += 1
        return cnt

    i_to_purs = True
    sr = (observation.get("self_role") or "").lower()
    orr = (observation.get("opponent_role") or "").lower()
    if ("evad" in sr) and ("purs" not in sr):
        i_to_purs = False
    if ("purs" in orr):
        i_to_purs = False if "purs" in sr else i_to_purs

    best_move = [0, 0]
    best_val = -10**18
    # Predict opponent mobility: fewer options is better for pursuer (worse for evader).
    opp_mob = legal_moves_count(ox, oy)
    # Block line preference: move into a cell that reduces relative vector components.
    vx, vy = ox - sx, oy - sy
    step_x = 0 if vx == 0 else (1 if vx > 0 else -1)
    step_y = 0 if vy == 0 else (1 if vy > 0 else -1)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if nx == ox and ny == oy:
            val = 10**12
        else:
            dist = d2(nx, ny, ox, oy)
            # Move should generally align with chasing direction.
            align = 0
            if dx == step_x:
                align += 1
            if dy == step_y:
                align += 1
            # Penalize proximity to obstacles (avoid getting cornered ourselves).
            pen_obs = obstacle_near(nx, ny)
            # Attempt to reduce opponent options by approaching in a way that makes escape harder.
            # Approx: if we move close, assume opponent mobility decreases with our distance.
            mob_effect = (opp_mob * 5) / (1 + int(dist))
            val = 0
            if i_to_purs:
                val = (-dist * 20) + (align * 3) - (pen_obs * 2) + (-mob_effect * 50)
            else:
                # If mis-assigned, invert objective deterministically (maximize survival).
                val = (dist * 20) + (align * 3) - (pen_obs * 2) + (mob_effect * 50)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move