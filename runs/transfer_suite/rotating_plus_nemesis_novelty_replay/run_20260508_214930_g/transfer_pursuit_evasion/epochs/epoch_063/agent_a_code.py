def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    is_evader = "evader" in (observation.get("self_role", "") or "").lower()
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = [(dx, dy) for dx, dy in deltas if 0 <= sx + dx < w and 0 <= sy + dy < h and (sx + dx, sy + dy) not in obs]

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def free_neighbor_count(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                c += 1
        return c

    def in_corner_bias(x, y):
        # Encourage evader to stick to farther corner; pursuer to occupy nearer corner.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        dists = [manhattan(x, y, cx, cy) for cx, cy in corners]
        if is_evader:
            target_corner = max(corners, key=lambda c: manhattan(c[0], c[1], ox, oy))
        else:
            target_corner = min(corners, key=lambda c: manhattan(c[0], c[1], ox, oy))
        return -manhattan(x, y, target_corner[0], target_corner[1])

    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        dist = manhattan(nx, ny, ox, oy)
        fnc = free_neighbor_count(nx, ny)

        if is_evader:
            # Maximize distance; then maximize mobility; then move toward far corner.
            score = (dist * 1000) + (fnc * 10) + in_corner_bias(nx, ny)
        else:
            # Minimize distance; then reduce opponent escape (fewer mobility cells for evader);
            # also bias toward nearer corner to constrain.
            score = (-dist * 1000) + (-fnc * 5) + in_corner_bias(nx, ny)

        # Deterministic tie-break: lexicographic on (dx, dy) for identical scores
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]