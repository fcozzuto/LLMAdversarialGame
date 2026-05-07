def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    obstacles = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)
    resources = observation.get("resources", []) or []
    resources = [(p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2]
    resset = set(resources)
    if (sx, sy) in resset:
        return [0, 0]

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        return [0, 0]

    # Choose resource where we have the best distance advantage; then move toward it.
    best_move = None
    best_score = None
    for mdx, mdy in legal:
        nx, ny = sx + mdx, sy + mdy
        # If stepping onto a resource, take it.
        if (nx, ny) in resset:
            return [mdx, mdy]

        chosen_adv = None
        chosen_dist = None
        for rx, ry in resources:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            adv = od - sd  # higher means we get there first
            # Primary: distance advantage, Secondary: closer distance, Tertiary: stable tie-break.
            key = (adv, -sd, -((rx + 3 * ry) & 1023))
            if chosen_adv is None or (key > (chosen_adv, chosen_dist, 0)):
                chosen_adv = key[0]
                chosen_dist = -key[1]

        # Convert to scalar; also slightly prefer reducing our own distance overall.
        local_score = chosen_adv * 1000 - chosen_dist
        if best_score is None or local_score > best_score:
            best_score = local_score
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]