def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_type(x, y):
        p = (x, y)
        if p in obstacles:
            return "obs"
        if p in self_t:
            return "self"
        if p in opp_t:
            return "opp"
        if p in unclaimed:
            return "unclaimed"
        return "other"

    def adj_to_set(x, y, tset):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if inside(nx, ny) and (nx, ny) in tset:
                        return True
        return False

    actions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    # Heuristic targets: unclaimed cells adjacent to opponent territory; else expand toward unclaimed adjacent to us.
    prefer_contest = [(x, y) for (x, y) in unclaimed if adj_to_set(x, y, opp_t)]
    prefer_expand = [(x, y) for (x, y) in unclaimed if adj_to_set(x, y, self_t)]
    target_list = prefer_contest if prefer_contest else (prefer_expand if prefer_expand else list(unclaimed))

    # Deterministic tie-breaker order: smaller dx, then smaller dy.
    for dx, dy in sorted(actions, key=lambda a: (a[0], a[1])):
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        t = cell_type(nx, ny)
        # Base values
        score = 0
        if t == "opp":
            score += 140  # direct flip pressure
        elif t == "unclaimed":
            score += 60
        elif t == "self":
            score += 5
        else:
            score += 0

        # Tactical adjacency
        if t != "obs" and adj_to_set(nx, ny, opp_t):
            score += 35
        if adj_to_set(nx, ny, self_t):
            score += 10

        # Path direction: move toward nearest target (or nearest opp cell if no unclaimed)
        if target_list:
            tx, ty = min(target_list, key=lambda p: (p[0] - nx) ** 2 + (p[1] - ny) ** 2)
            dist2 = (tx - nx) ** 2 + (ty - ny) ** 2
            score += 40 - min(40, dist2 // 2)
        else:
            score += 5 - (abs(ox - nx) + abs(oy - ny))

        # Avoid drifting too far from the contested frontier when possible
        if prefer_contest:
            # Prefer cells that get closer to opponent position as a proxy for edge-pressuring.
            score += (abs(ox - sy) + abs(oy - sx)) - (abs(ox - ny) + abs(oy - nx))

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best