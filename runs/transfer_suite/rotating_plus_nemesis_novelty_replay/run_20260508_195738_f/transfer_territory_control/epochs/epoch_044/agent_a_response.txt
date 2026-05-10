def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def min_dist_to_set(nx, ny, s):
        if not s:
            return 99
        md = 99
        for px, py in s:
            d = abs(px - nx) + abs(py - ny)
            if d < md:
                md = d
        return md

    best_score = -10**18
    best_move = (0, 0)

    my_dist = min_dist_to_set(x, y, opp)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        cell_in_opp = (nx, ny) in opp
        cell_unclaimed = (nx, ny) in unclaimed
        cell_in_me = (nx, ny) in selft

        if cell_in_me:
            base = 0.0
        elif cell_unclaimed:
            base = 1.0
        elif cell_in_opp:
            base = 0.9  # will flip on entry
        else:
            base = 0.1  # should be rare

        # Encourage consolidation and safer expansion away from opponent frontier
        adj_me = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if inb(ax, ay) and (ax, ay) in selft:
                    adj_me += 1

        opp_d = min_dist_to_set(nx, ny, opp)
        delta_from_current = opp_d - my_dist

        # Prefer increases in distance from opponent, but allow captures when close.
        risk_penalty = -0.08 * (8 - min(8, opp_d)) if opp else 0.0
        capture_bonus = 0.35 if cell_in_opp and opp_d <= 3 else 0.0
        forward = base + 0.12 * adj_me + 0.25 * delta_from_current + capture_bonus + risk_penalty

        if forward > best_score or (forward == best_score and (dx, dy) < best_move):
            best_score = forward
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]