def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    w, h = int(observation.get("grid_width", 8)), int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    res = [(int(r[0]), int(r[1])) for r in resources]
    res.sort()

    best = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue

        val = 0
        for i, (tx, ty) in enumerate(res):
            ds = man(nx, ny, tx, ty)
            do = man(ox, oy, tx, ty)
            # Strongly prefer resources we can reach first (or tie), with distance as secondary.
            # Small deterministic bias on earlier resources in sorted order.
            if ds <= do:
                val += 1000 - ds * 5 - i
            else:
                # If opponent is much closer, discourage; but still allow if we are close too.
                val -= (do - ds) * 25 + (ds) * 2 + i // 2

        # Prefer actions that move toward a promising target (adds stability).
        if res:
            tx, ty = res[0]
            val += -(man(nx, ny, tx, ty))

        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]