def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
    else:
        # Pick a contested resource where we are relatively earlier than opponent
        best = None
        best_key = None
        for rx, ry in resources:
            sd = abs(rx - sx) + abs(ry - sy)
            od = abs(rx - ox) + abs(ry - oy)
            # Primary: maximize lead (od - sd). Secondary: minimize our distance.
            key = (od - sd, -sd)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    best_move = (0, 0)
    best_val = None

    # Evaluate candidate steps: prefer reducing our distance to target,
    # while not allowing opponent to become much closer to the same target.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        my_dist = abs(tx - nx) + abs(ty - ny)
        opp_dist = abs(tx - ox) + abs(ty - oy)

        # After we move, opponent might also act next; approximate by using
        # our new distance vs their current distance as a lead estimate.
        lead = opp_dist - my_dist

        # Deterministic tie-breaking: prefer moves that also keep us farther from opponent.
        away = (abs(nx - ox) + abs(ny - oy))

        val = (lead, -my_dist, away, -abs(dx) - abs(dy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]