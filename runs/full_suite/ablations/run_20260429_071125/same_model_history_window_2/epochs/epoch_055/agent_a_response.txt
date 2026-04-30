def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # First pick a deterministic "best target" based on who can arrive first, then evaluate each move toward it.
    resources.sort()
    best_target = resources[0]
    best_val = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer targets where we are closer; also prefer those where opponent is significantly farther.
        val = (do - ds) * 10 - ds
        if best_val is None or val > best_val or (val == best_val and (tx, ty) < best_target):
            best_val = val
            best_target = (tx, ty)

    tx, ty = best_target

    # Local obstacle "pressure": discourage stepping near obstacles.
    def obs_pressure(x, y):
        pr = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    pr += 1
        return pr

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        ds_next = cheb(nx, ny, tx, ty)
        # Add a "race" term: if opponent is already closer to the same target, prioritize minimizing the advantage gap.
        do_to_target = cheb(ox, oy, tx, ty)
        gap = do_to_target - ds_next

        # Small tie-breakers for determinism and stability.
        score = gap * 10 - ds_next - obs_pressure(nx, ny) * 0.5

        # If opponent might snatch a nearer alternative, lightly consider moving that also improves best resource capture.
        # Deterministic: compare against a single alternate resource (the next in sorted order).
        alt = resources[1] if len(resources) > 1 else best_target
        ax, ay = alt
        ds_alt = cheb(nx, ny, ax, ay)
        do_alt = cheb(ox, oy, ax, ay)
        alt_score = (do_alt - ds_alt) * 6 - ds_alt
        score += alt_score * 0.15

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]