def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    self_cells = set(tuple(c) for c in (observation.get("self_territory") or []))
    opp_cells = set(tuple(c) for c in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(c) for c in (observation.get("unclaimed_cells") or []))

    unclaimed_list = list(unclaimed)
    if not unclaimed_list:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                x, y = sx + dx, sy + dy
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles and (x, y) in unclaimed:
                    unclaimed_list = [(x, y)]
                    break
            if unclaimed_list:
                break

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs = moves  # deterministic

    def dist_manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def nearest_dist(cells, pos):
        if not cells:
            return 999
        best = 999
        for t in cells:
            d = dist_manh(t, pos)
            if d < best:
                best = d
        return best

    # Prefer counter-claiming: cells adjacent to opponent territory are high priority.
    opp_adj = set()
    for (x, y) in opp_cells:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    if (nx, ny) not in opp_cells:
                        opp_adj.add((nx, ny))

    opp_adj_list = list(opp_adj)
    if not opp_adj_list:
        opp_adj_list = list(opp_cells)

    best_move = (0, 0)
    best_val = -10**18
    # Deterministic tie-break: first move in dirs ordering that reaches best_val
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        nxt = (nx, ny)

        val = 0.0
        if nxt in opp_cells:
            val += 8.0  # immediate flip on entry (very strong)
        if nxt in unclaimed:
            val += 3.0  # secure new territory
        if nxt in self_cells:
            val += 1.0  # maintain pressure / avoid wasting turns

        # Move toward opponent frontier / high-likelihood flip targets
        d_front = nearest_dist(opp_adj_list, nxt)
        val += -0.35 * d_front

        # Avoid moving away from both targets (slight stabilizer)
        d_uncl = nearest_dist(unclaimed_list, nxt) if unclaimed_list else 0
        val += -0.12 * d_uncl

        # Prefer not to get stuck: small penalty for staying
        if dx == 0 and dy == 0:
            val -= 0.2

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]