def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]
    obs = set((p[0], p[1]) for p in obstacles)
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            continue
        # If we land on a resource, prioritize strongly.
        if any(nx == rx and ny == ry for rx, ry in resources):
            val = 1e9
        else:
            val = -10**9
            for rx, ry in resources:
                sd = abs(nx - rx) + abs(ny - ry)
                od = abs(ox - rx) + abs(oy - ry)
                # Material advantage: resources where opponent is farther.
                # Add slight bias to reduce our distance even if opponent is also close.
                advantage = (od - sd)
                cand = advantage * 100 - sd
                if cand > val:
                    val = cand
            # Small extra: prefer moving away from obstacles is implicit; also discourage moving toward opponent.
            dist_to_opp = abs(nx - ox) + abs(ny - oy)
            val += dist_to_opp * 0.1
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]