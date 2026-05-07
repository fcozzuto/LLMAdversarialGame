def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def man(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_dx, best_dy = 0, 0
    best_val = -10**18

    # Deterministic tie-break: prefer moves with smaller (dx,dy) in lexicographic order later by <= checks.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Soft obstacle avoidance: discourage being adjacent to obstacles.
        adj_obs = 0
        for obx, oby in obstacles:
            if man(nx, ny, obx, oby) == 1:
                adj_obs += 1

        move_val = 0
        # Score each resource by: (opponent distance - my distance), with urgency.
        # Also slightly prefer closer resources overall.
        min_my = 10**9
        min_op = 10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            if ds < min_my: min_my = ds
            if do < min_op: min_op = do
            lead = do - ds  # positive if we are closer
            # Urgency favors catching soon; deny favors pushing lead negative/less.
            urgency = 20 if ds == 0 else 0
            move_val = max(move_val, lead * 10 - ds - adj_obs * 3 + urgency)

        # If no resource was evaluated (shouldn't happen), fall back to moving toward nearest.
        if move_val == 0:
            move_val = -min_my - adj_obs * 3

        # Extra shaping: reduce distance to the currently most contested resource relative to opponent.
        # Pick deterministically the resource that maximizes (do - ds) from our candidate.
        contested = -10**18
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            contested = max(contested, do - ds)
        move_val += contested * 1.5

        if move_val > best_val or (move_val == best_val and (dx, dy) < (best_dx, best_dy)):
            best_val = move_val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]