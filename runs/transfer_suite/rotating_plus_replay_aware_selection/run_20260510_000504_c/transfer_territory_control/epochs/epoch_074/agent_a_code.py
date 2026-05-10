def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    resources = observation.get("resources") or []
    if resources:
        tx, ty = resources[0]
    else:
        best = None
        if self_terr:
            for (x, y) in self_terr:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if dx == 0 and dy == 0: 
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < w and 0 <= ny < h and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                            d = abs(nx - sx) + abs(ny - sy)
                            if best is None or d < best[0]:
                                best = (d, nx, ny)
        if best is None and opp_terr:
            for (x, y) in opp_terr:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < w and 0 <= ny < h and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                            # Prefer cells close to opponent to challenge center-claim
                            d = abs(nx - sx) + abs(ny - sy) + 2 * (abs(nx - x) + abs(ny - y))
                            if best is None or d < best[0]:
                                best = (d, nx, ny)
        if best is None:
            if unclaimed:
                # Go to nearest unclaimed not blocked
                for (nx, ny) in unclaimed:
                    if (nx, ny) in obstacles: 
                        continue
                    d = abs(nx - sx) + abs(ny - sy)
                    if best is None or d < best[0]:
                        best = (d, nx, ny)
        if best is None:
            return [0, 0]
        tx, ty = best[1], best[2]

    # Choose move that reduces Manhattan distance, avoiding obstacles if possible
    best_move = (10**9, 0, 0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            # tie-break: prefer diagonal/forward progress toward target
            tie = 0 if (dx == 0 or dy == 0) else -0.1
            if d + tie < best_move[0]:
                best_move = (d + tie, dx, dy)

    if best_move[0] == 10**9:
        return [0, 0]
    dx, dy = best_move[1], best_move[2]
    return [int(dx), int(dy)]