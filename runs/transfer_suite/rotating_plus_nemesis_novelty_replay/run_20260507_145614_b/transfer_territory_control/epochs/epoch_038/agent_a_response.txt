def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p[:2]) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    unclaimed = [tuple(p[:2]) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2]
    unclaimed_set = set(unclaimed)
    res = set(tuple(p[:2]) for p in (observation.get("resources") or []) if p and len(p) >= 2)

    self_t = set(tuple(p[:2]) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_t = set(tuple(p[:2]) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Prefer unclaimed cells adjacent to our territory (fast, hard to counter)
    cand = []
    for x, y in unclaimed:
        if (x, y) in obstacles:
            continue
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (x + ax, y + ay) in self_t:
                    cand.append((x, y))
                    ax = ay = None
                    break
            if len(cand) and cand[-1] == (x, y):
                break

    target_list = cand if cand else (unclaimed if unclaimed else list(res) if res else [opp_t.pop() if opp_t else (ox, oy)])
    if not target_list:
        target_list = [(ox, oy)]

    # Precompute nearest target distances (Manhattan)
    def nearest_dist(x, y):
        best = 10**9
        for tx, ty in target_list:
            d = abs(tx - x) + abs(ty - y)
            if d < best:
                best = d
        return best

    # If we are near opponent territory, try to step into it to flip
    near_opp = []
    for px, py in [(sx + dx, sy + dy) for dx, dy in dirs if not (dx == 0 and dy == 0)]:
        if valid(px, py) and (px, py) in opp_t:
            near_opp.append((px, py))

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if (nx, ny) in opp_t:
            base = 30
        elif (nx, ny) in unclaimed_set:
            base = 12
        elif (nx, ny) in self_t:
            base = 2
        else:
            base = 4  # other empty/unknown-like cells

        # Slightly bias towards resources if visible
        if (nx, ny) in res:
            base += 6

        # Main shaping: move closer to target frontier
        d = nearest_dist(nx, ny)
        score = base - d

        # Extra deterministic tie-break: prefer moves that reduce distance to opponent if we're contesting
        score += (abs(nx - ox) + abs(ny - oy)) * (-0.01)

        # Strongly prefer direct counterclaim into adjacent opponent territory when available
        if near_opp and (nx, ny) in opp_t:
            score += 50

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]