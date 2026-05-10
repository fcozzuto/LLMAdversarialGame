def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for x, y in obstacles:
        if inb(x, y):
            obs.add((x, y))

    my_set = set(tuple(p) for p in (observation.get("self_territory") or []))
    op_set = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    un_set = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    un_list = [p for p in un_set if inb(p[0], p[1])]
    if not un_list:
        un_list = [p for p in op_set if inb(p[0], p[1])]
    if not un_list:
        return [0, 0]

    def md(x, y, p):
        return abs(x - p[0]) + abs(y - p[1])

    best_move = (0, 0)
    best_score = -10**18

    # Precompute 8 nearest unclaimed targets to avoid heavy search
    dists = []
    for p in un_list:
        d = md(ax, ay, p)
        dists.append((d, p))
    dists.sort(key=lambda t: (t[0], t[1][1], t[1][0]))
    nearest = [p for _, p in dists[:8]]

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = ax, ay
            dx, dy = 0, 0

        # Base reward by immediate capture value
        if (nx, ny) in un_set:
            base = 30
        elif (nx, ny) in op_set:
            base = 18
        elif (nx, ny) in my_set:
            base = 6
        else:
            base = 3

        # Encourage moves that reduce distance to frontier (unclaimed)
        # If entering opponent territory, require it to also improve frontier distance.
        new_best = min(md(nx, ny, p) for p in nearest)
        old_best = min(md(ax, ay, p) for p in nearest)
        frontier_delta = old_best - new_best  # positive is good

        score = base + 4 * frontier_delta

        # Penalize stepping into opponent without frontier progress
        if (nx, ny) in op_set and frontier_delta <= 0:
            score -= 10

        # Mild penalty for stagnation unless it is improving frontier distance
        if (dx, dy) == (0, 0) and frontier_delta <= 0:
            score -= 6

        if score > best_score or (score == best_score and (dx, dy) == (0, 0)):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]