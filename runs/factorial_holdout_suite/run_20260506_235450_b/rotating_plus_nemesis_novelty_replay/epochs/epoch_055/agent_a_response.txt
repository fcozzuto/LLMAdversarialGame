def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation.get("opponent_position", (None, None))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            obstacles.add((p[0], p[1]))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Fixed move priority to keep determinism
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose the resource that maximizes our eventual advantage over opponent
    best_target = None
    best_val = -10**18
    for r in resources:
        rx, ry = r
        our_d = abs(sx - rx) + abs(sy - ry)
        opp_d = abs(ox - rx) + abs(oy - ry) if (ox is not None and oy is not None) else 10**6
        # Higher is better: immediate advantage if we race to it
        val = (opp_d - our_d) * 5 - our_d
        if val > best_val:
            best_val = val
            best_target = (rx, ry)

    # If something goes wrong, just stay put
    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Move scoring: get closer to chosen target while maintaining advantage
        our_d = abs(nx - tx) + abs(ny - ty)
        opp_d = abs(ox - tx) + abs(oy - ty) if (ox is not None and oy is not None) else 10**6
        advantage = opp_d - our_d

        # Extra nudge: avoid moving closer to opponent when racing is tight
        tight_penalty = 0
        if ox is not None and oy is not None:
            tight_penalty = max(0, (abs(nx - tx) + abs(ny - ty)) - (abs(ox - tx) + abs(oy - ty))) * 2

        score = advantage * 10 - our_d - tight_penalty

        # If we land on a resource, prioritize strongly
        if (nx, ny) in set((r[0], r[1]) for r in resources):
            score += 10**9

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]