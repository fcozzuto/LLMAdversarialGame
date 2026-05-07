def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_in = observation.get("obstacles") or []

    obstacles = set()
    for p in obstacles_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if resources:
        # Pick the most contestable resource: prioritize where we can be earlier than opponent.
        best_r = None
        best_gap = None  # (opp_dist - our_dist) higher is better
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ug = man(sx, sy, rx, ry)
            og = man(ox, oy, rx, ry)
            gap = og - ug
            if best_gap is None or gap > best_gap or (gap == best_gap and ug < best_gap_us):
                best_gap = gap
                best_gap_us = ug
                best_r = (rx, ry)
        if best_r is None:
            best_r = resources[0]
        rx, ry = best_r
    else:
        rx, ry = ox, oy

    best_move = (0, 0)
    best_val = None
    # Deterministic small tie-break: prefer lower (abs(dx)+abs(dy)) then lexicographic dx,dy
    for dx, dy, nx, ny in moves:
        our_d = man(nx, ny, rx, ry)
        opp_d = man(nx, ny, ox, oy)  # influence
        # For contesting, also measure opponent distance to same target
        opp_target_d = man(ox, oy, rx, ry)
        val = 0
        if resources:
            # Want to get closer than opponent; also keep away from wandering.
            val += (opp_target_d - our_d) * 10
            val -= our_d
            # Slightly favor moving toward our target while not giving opponent too much advantage in distance-to-us
            val += (man(ox, oy, nx, ny) - man(ox, oy, sx, sy)) * 1
        else:
            # No resources visible: drift toward opponent to force interference
            val += opp_d * (-1)

        tie = (abs(dx) + abs(dy), dx, dy)
        if best_val is None or val > best_val or (val == best_val and tie < best_tie):
            best_val = val
            best_tie = tie
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]