def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    turns_remaining = int(observation.get("turns_remaining", 0) or 0)
    rem = observation.get("remaining_resource_count", None)
    rem = int(rem) if rem is not None else len(resources)

    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Early: race; Late: deny opponent.
    k_deny = 0.35 if rem <= 6 else 0.15
    k_time = 0.02 if rem <= 6 else 0.0

    best = (-10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        best_res = 10**9
        best_score = -10**18
        for rx, ry in resources:
            d_me = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            # Prefer closer resources; add deny term (opp distance advantage).
            score = -(d_me) + k_deny * (d_op - d_me) + k_time * (d_op - d_me)
            if score > best_score:
                best_score = score
                best_res = d_me
        # Tie-break: smaller best_res (closer), then deterministic delta order
        key = (best_score, -best_res, -dx, -dy)
        if key > (best[0], -best[1], -best[2], -best[2]):
            best = (best_score, dx, dy)

    return [int(best[1]), int(best[2])]