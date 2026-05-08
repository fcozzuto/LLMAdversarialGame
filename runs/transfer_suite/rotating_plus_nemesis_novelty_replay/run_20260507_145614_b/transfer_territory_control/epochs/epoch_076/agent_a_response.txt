def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    opp_set = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_set.add((x, y))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    if not unclaimed:
        return [0, 0]

    def adj_to_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in opp_set:
                    return True
        return False

    # pick target deterministically: prefer unclaimed adjacent to opponent territory, else nearest unclaimed
    best = None
    for c in unclaimed:
        x, y = c
        if adj_to_opp(x, y):
            key = (0, abs(x - sx) + abs(y - sy), x, y)
        else:
            key = (1, abs(x - sx) + abs(y - sy), x, y)
        if best is None or key < best[0]:
            best = (key, c)
    tx, ty = best[1]

    candidates = [(-1, -1), (0, -1), (1, -1),
                  (-1, 0),  (0, 0),  (1, 0),
                  (-1, 1),  (0, 1),  (1, 1)]

    def heuristic(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        d = abs(nx - tx) + abs(ny - ty)
        if (nx, ny) in opp_set:
            return 1000 - 5 * d
        # encourage claiming unclaimed edge cells; slightly prefer opponent-adjacent squares
        if (nx, ny) in unclaimed:
            bonus = 200
        else:
            bonus = 0
        if bonus == 0 and adj_to_opp(nx, ny):
            bonus = 40
        return bonus - 3 * d

    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            sc = heuristic(nx, ny)
            if sc > best_score:
                best_score = sc
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]