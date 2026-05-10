def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}

    def man(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Pick a small deterministic subset of promising resources
    res_sorted = sorted(resources, key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))
    best_subset = res_sorted[:3] if len(res_sorted) > 3 else res_sorted

    cur_block = (sx, sy) in obst
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            v = -10**15
        else:
            v = 0.0
            # Greedy multi-resource lookahead: maximize our lead after the move, with denial against opponent
            for rx, ry in best_subset:
                ds = man(nx, ny, rx, ry)
                do = man(ox, oy, rx, ry)
                # Prioritize being able to take first; break ties with closeness to the resource
                lead = do - ds
                take = 1.5 if (nx, ny) == (rx, ry) else 0.0
                # Also avoid moving into squares that reduce opponent's advantage on the closest target
                v += take + 2.2 * lead - 0.15 * ds
            # Mild penalty for moves that stray far from all promising resources
            v -= 0.02 * man(nx, ny, best_subset[0][0], best_subset[0][1])
            # Determinism tweak: prefer moves with smaller lexicographic delta when values tie
        if (v > best_val) or (v == best_val and [dx, dy] < best_move):
            best_val = v
            best_move = [dx, dy]

    if cur_block and best_move == [0, 0]:
        # If somehow on obstacle (shouldn't happen), try to step out deterministically
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                return [dx, dy]
        return [0, 0]

    return [int(best_move[0]), int(best_move[1])]