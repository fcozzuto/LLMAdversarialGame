def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def get_xy(v, default=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return (int(p[0]), int(p[1]))
        return default

    sx, sy = get_xy(observation.get("self_position", None), (0, 0))
    ox, oy = get_xy(observation.get("opponent_position", None), (sx, sy))

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        x, y = get_xy(o, None) if isinstance(o, (list, tuple, dict)) else (None, None)
        if x is None:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        x, y = get_xy(r, None) if isinstance(r, (list, tuple, dict)) else (None, None)
        if x is None:
            continue
        if free(x, y):
            resources.append((x, y))

    if not resources:
        # Step toward opponent if no resources.
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    neigh = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Avoid invalid moves by engine, but ensure determinism by skipping blocked destinations when possible.
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            # Still allow, but penalize strongly to prefer legal moves.
            nx, ny = sx, sy
            illegal = True
        else:
            illegal = False

        # Choose resource that we likely win: maximize (opp_dist - self_dist) and closeness.
        local_best = -10**18
        for tx, ty in resources:
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            # Penalize moving away; reward improving our distance; prefer shorter ties.
            score = (od - sd) * 100 - sd * 3 - (od * 0.5)
            # Prefer targets that are closer to completion for us.
            if sd == 0:
                score += 10**6
            # Small preference for moving toward center of action (resource proximity).
            score += -abs((tx - (w - 1) / 2)) * 0.01 - abs((ty - (h - 1) / 2)) * 0.01
            if score > local_best:
                local_best = score

        # If we selected an illegal move, reduce.
        if illegal:
            local_best -= 10**6

        # Tie-break deterministically: prefer smaller dx then dy magnitude, then stay.
        tie = (0 if local_best > best_score else 1)
        if local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)
        elif local_best == best_score:
            cand = (abs(dx), abs(dy), dx != 0 or dy != 0)
            cur = (abs(best_move[0]), abs(best_move[1]), best_move[0] != 0 or best_move[1] != 0)
            if cand < cur:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]