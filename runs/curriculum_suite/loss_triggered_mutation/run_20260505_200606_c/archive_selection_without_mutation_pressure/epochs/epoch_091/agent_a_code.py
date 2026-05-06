def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if (rx, ry) not in obstacles:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_dx, best_dy = 0, 0
    best_val = -10**18
    do_cur_cache = {}
    for rx, ry in res:
        do_cur_cache[(rx, ry)] = man(ox, oy, rx, ry)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        total = 0
        for rx, ry in res:
            ds = man(nx, ny, rx, ry)
            do = do_cur_cache[(rx, ry)]
            if ds == 0:
                total += 10**7
                continue

            if ds <= do:
                # Claim/beat: large reward for margin, mild preference for closeness
                margin = do - ds
                # Disruption: move that makes opponent farther from this resource than from current position
                # (opponent next turn unknown; use heuristic: if we move closer, opponent likely still not closer)
                do_next_proxy = min(do + 1, man(ox, oy, rx, ry) + 1)
                disruption = do - do_next_proxy
                total += margin * 250 - ds * 4 + disruption * 3
            else:
                # If we can't beat it, still steer to reduce opponent best options
                total += (do - ds) * 2 - ds * 1

        # Small tie-break to reduce oscillation deterministically
        total -= (abs(dx) + abs(dy)) * 0.5
        if total > best_val:
            best_val = total
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]