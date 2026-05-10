def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # Prefer center pressure: target cells closest to opponent centroid among (opponent_territory ∪ unclaimed)
    if opp:
        sx = 0.0
        sy = 0.0
        n = len(opp)
        for px, py in opp:
            sx += px
            sy += py
        cx = sx / n
        cy = sy / n
    else:
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0

    candidates = []
    # Limit candidates for speed deterministically
    # Take up to 24 closest-by-centroid cells from opp, then from unclaimed
    opp_list = list(opp)
    opp_list.sort(key=lambda p: (abs(p[0] - cx) + abs(p[1] - cy), abs(p[0] - x) + abs(p[1] - y), p[0], p[1]))
    candidates.extend(opp_list[:12])
    un_list = list(unclaimed)
    un_list.sort(key=lambda p: (abs(p[0] - cx) + abs(p[1] - cy), abs(p[0] - x) + abs(p[1] - y), p[0], p[1]))
    candidates.extend(un_list[:12])

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Immediate pressure value
        cell_in_opp = (nx, ny) in opp
        cell_unclaimed = (nx, ny) in unclaimed
        immediate = 0.0
        if cell_in_opp:
            immediate += 2.0
        if cell_unclaimed:
            immediate += 1.0

        # Aim toward centroid by moving closer to best candidate (distance heuristic)
        if candidates:
            dist = min(abs(nx - tx) + abs(ny - ty) for tx, ty in candidates)
        else:
            dist = abs(nx - cx) + abs(ny - cy)

        # Extra tie-break: slightly prefer diagonal moves toward center
        center_bias = -0.01 * (abs(nx - cx) + abs(ny - cy))
        stay_penalty = -0.03 if (dx == 0 and dy == 0) else 0.0

        val = immediate - 0.35 * dist + center_bias + stay_penalty
        if val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
            best_val = val
            best_move = [dx, dy]

    return best_move