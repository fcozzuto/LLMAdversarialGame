def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-breaking order already in moves list.
    best = None
    best_score = -10**18

    # Precompute: opponent distances to resources for scoring.
    op_dist = {}
    for r in resources:
        if inb(r[0], r[1]) and tuple(r) not in obstacles:
            op_dist[(r[0], r[1])] = cheb((ox, oy), (r[0], r[1]))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            # Engine will keep us in place; still consider as [0,0] effect by using (sx,sy).
            nx, ny = sx, sy
        # Move scoring: prefer resources we can reach sooner, especially where opponent is far.
        my_better = 10**9
        block = 0
        for r in resources:
            rx, ry = r[0], r[1]
            if not inb(rx, ry) or (rx, ry) in obstacles:
                continue
            md = cheb((nx, ny), (rx, ry))
            od = op_dist.get((rx, ry), 10**9)
            if md < my_better:
                my_better = md
            # Higher is better: reward being relatively closer than opponent.
            block = max(block, (od - md))
        # Primary objective: minimize my_better; secondary: maximize block (steal/block priority).
        # Convert to single score; constants tuned for stability.
        score = (-my_better) * 1000 + block
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]